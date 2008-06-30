"""\
@file runloop.py
@author Bob Ippolito

Defines the core eventlet runloop. The runloop keeps track of scheduled
events and observers which watch for specific portions of the runloop to
be executed. 

Copyright (c) 2005-2006, Bob Ippolito
Copyright (c) 2007, Linden Research, Inc.
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import time
import bisect
import sys
import traceback

import greenlet

from eventlet.timer import Timer


class RunLoop(object):
    SYSTEM_EXCEPTIONS = (KeyboardInterrupt, SystemExit)
    
    def __init__(self, wait=None, clock=None):
        if clock is None:
            clock = self.default_clock()
        self.clock = clock
        if wait is None:
            wait = self.default_wait
        self.wait = wait
        self.stopping = False
        self.running = False
        self.timers = []
        self.timers_by_greenlet = {}
        self.next_timers = []
        self.observers = {}
        self.observer_modes = {
            'entry': [],
            'before_timers': [],
            'before_waiting': [],
            'after_waiting': [],
            'exit': [],
        }

    def default_wait(self, time):
        return None
        
    def default_clock(self):
        return time.time

    def default_sleep(self):
        return 60.0

    def sleep_until(self):
        t = self.timers
        if not t:
            return None
        return t[0][0]
        
    def run(self):
        """Run the runloop until abort is called.
        """
        if self.running:
            raise RuntimeError("Already running!")
        try:
            self.running = True
            self.stopping = False
            self.fire_observers('entry')
            while not self.stopping:
                self.prepare_timers()
                self.fire_observers('before_timers')
                self.fire_timers(self.clock())
                self.prepare_timers()
                wakeup_when = self.sleep_until()
                if wakeup_when is None:
                    sleep_time = self.default_sleep()
                else:
                    sleep_time = wakeup_when - self.clock()
                if sleep_time > 0:
                    self.fire_observers('before_waiting')
                    self.wait(sleep_time)
                    self.fire_observers('after_waiting')
                else:
                    self.wait(0)
            else:
                del self.timers[:]
                del self.next_timers[:]
            self.fire_observers('exit')
        finally:
            self.running = False
            self.stopping = False

    def abort(self):
        """Stop the runloop. If run is executing, it will exit after completing
        the next runloop iteration.
        """
        if self.running:
            self.stopping = True

    def add_observer(self, observer, *modes):
        """Add an event observer to this runloop with the given modes.
        Valid modes are:
            entry: The runloop is being entered.
            before_timers: Before the expired timers for this iteration are executed.
            before_waiting: Before waiting for the calculated wait_time
                where nothing will happen.
            after_waiting: After waiting, immediately before starting the top of the
                runloop again.
            exit: The runloop is exiting.

        If no mode is passed or mode is all, the observer will be fired for every
        event type.
        """
        if not modes or modes == ('all',):
            modes = tuple(self.observer_modes)
        self.observers[observer] = modes
        for mode in modes:
            self.observer_modes[mode].append(observer)

    def remove_observer(self, observer):
        """Remove a previously registered observer from all event types.
        """
        for mode in self.observers.pop(observer, ()):
            self.observer_modes[mode].remove(observer)
            
    def squelch_observer_exception(self, observer, exc_info):
        traceback.print_exception(*exc_info)
        print >>sys.stderr, "Removing observer: %r" % (observer,)
        self.remove_observer(observer)
        
    def fire_observers(self, activity):
        for observer in self.observer_modes[activity]:
            try:
                observer(self, activity)
            except self.SYSTEM_EXCEPTIONS:
                raise
            except:
                self.squelch_observer_exception(observer, sys.exc_info())

    def squelch_timer_exception(self, timer, exc_info):
        traceback.print_exception(*exc_info)
        print >>sys.stderr, "Timer raised: %r" % (timer,)

    def _add_absolute_timer(self, when, info):
        # the 0 placeholder makes it easy to bisect_right using (now, 1)
        self.next_timers.append((when, 0, info))

    def add_timer(self, timer):
        scheduled_time = self.clock() + timer.seconds
        self._add_absolute_timer(scheduled_time, timer)
        current_greenlet = greenlet.getcurrent()
        if current_greenlet not in self.timers_by_greenlet:
            self.timers_by_greenlet[current_greenlet] = {}
        self.timers_by_greenlet[current_greenlet][timer] = True
        timer.greenlet = current_greenlet
        return scheduled_time


    def prepare_timers(self):
        ins = bisect.insort_right
        t = self.timers
        for item in self.next_timers:
            ins(t, item)
        del self.next_timers[:]

    def schedule_call(self, seconds, cb, *args, **kw):
        """Schedule a callable to be called after 'seconds' seconds have
        elapsed.
            seconds: The number of seconds to wait.
            cb: The callable to call after the given time.
            *args: Arguments to pass to the callable when called.
            **kw: Keyword arguments to pass to the callable when called.
        """
        t = Timer(seconds, cb, *args, **kw)
        self.add_timer(t)
        return t

    def fire_timers(self, when):
        t = self.timers
        last = bisect.bisect_right(t, (when, 1))
        i = 0
        for i in xrange(last):
            timer = t[i][2]
            try:
                try:
                    timer()
                except self.SYSTEM_EXCEPTIONS:
                    raise
                except:
                    self.squelch_timer_exception(timer, sys.exc_info())
            finally:
                try:
                    del self.timers_by_greenlet[timer.greenlet][timer]
                except KeyError:
                    pass
        del t[:last]

    def cancel_timers(self, greenlet):
        if greenlet not in self.timers_by_greenlet:
            return
        for timer in self.timers_by_greenlet[greenlet]:
            if not timer.cancelled and timer.seconds:
                ## If timer.seconds is 0, this isn't a timer, it's
                ## actually eventlet's silly way of specifying whether
                ## a coroutine is "ready to run" or not.
                timer.cancel()
                print 'Runloop cancelling left-over timer %s' % timer
        del self.timers_by_greenlet[greenlet]
        
