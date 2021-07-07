# Hippolyzer

![Python Test Status](https://github.com/SaladDais/Hippolyzer/workflows/Run%20Python%20Tests/badge.svg) [![codecov](https://codecov.io/gh/SaladDais/Hippolyzer/branch/master/graph/badge.svg?token=HCTFA4RAXX)](https://codecov.io/gh/SaladDais/Hippolyzer)

[Hippolyzer](http://wiki.secondlife.com/wiki/Hippo) is a revival of Linden Lab's
[PyOGP library](http://wiki.secondlife.com/wiki/PyOGP)
targeting modern Python 3, with a focus on debugging issues in Second Life-compatible
servers and clients. There is a secondary focus on mocking up new features without requiring a
modified server or client.

Wherever reasonable, readability and testability are prioritized over performance.

Almost all code from PyOGP has been either rewritten or replaced. Major changes from
upstream include making sure messages always correctly round-trip, and the addition
of a debugging proxy similar to ye olde WinGridProxy.

It supports hot-reloaded addon scripts that can rewrite, inject or drop messages.
Also included are tools for working with SL-specific assets like the internal animation format,
and the internal mesh format.

It's quick and easy to bash together a script that does something useful if you're familiar
with low-level SL details. See the [Local Animation addon example](https://github.com/SaladDais/Hippolyzer/blob/master/addon_examples/local_anim.py).

![Screenshot of proxy GUI](https://github.com/SaladDais/Hippolyzer/blob/master/static/screenshot.png?raw=true)

## Setup

### From Source

* Python 3.8 or above is **required**. If you're unable to upgrade your system Python package due to
  being on a stable distro, you can use [pyenv](https://github.com/pyenv/pyenv) to create
  a self-contained Python install with the appropriate version.
* [Create a clean Python 3 virtualenv](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment)
  with `python -mvenv <virtualenv_dir>`
* Activate the virtualenv by running the appropriate activation script
* * Under Linux this would be something like `source <virtualenv_dir>/bin/activate`
* * Under Windows it's `<virtualenv_dir>\Scripts\activate.bat`
* Run `pip install hippolyzer`, or run `pip install -e .` in a cloned repo to install an editable version

### Binary Windows Builds

Binary Windows builds are available on the [Releases page](https://github.com/SaladDais/Hippolyzer/releases/).
I don't extensively test these, building from source is recommended.

## Proxy

A proxy is provided with both a CLI and Qt-based interface. The proxy application wraps a
custom SOCKS 5 UDP proxy, as well as an HTTP proxy based on [mitmproxy](https://mitmproxy.org/).

Multiple clients are supported at a time, and UDP messages may be injected in either
direction. The proxy UI was inspired by the Message Log and Message Builder as present in
the [Alchemy](https://github.com/AlchemyViewer/Alchemy) viewer.

### Proxy Setup

* Run the proxy with `hippolyzer-gui`
* * Addons can be loaded through the `File -> Manage Addons` menu or on the command-line like
    `hippolyzer-gui addon_examples/bezoscape.py`
* * If you want the command-line version, run `hippolyzer-cli`
* Install the proxy's HTTPS certificate by going to `File -> Install HTTPS Certs`
* * You can also install it with `hippolyzer-cli --setup-ca <path to your viewer settings dir>`.
    On Linux that would be `~/.firestorm_x64/` if you're using Firestorm.
* * Certificate validation can be disabled entirely through viewer debug setting `NoVerifySSLCert`,
    but is not recommended.

#### Windows

Windows viewers have broken SOCKS 5 proxy support. To work around that, you need to use a wrapper EXE that
can make the viewer to correctly talk to Hippolyzer. Follow the instructions on https://github.com/SaladDais/WinHippoAutoProxy
to start the viewer and run it through Hippolyzer.

The proxy should _not_ be configured through the viewer's own preferences panel, it won't work correctly.

#### OS X & Linux

SOCKS 5 works correctly on these platforms, so you can just configure it through the
`preferences -> network -> proxy settings` panel:

* Start the viewer and configure it to use `127.0.0.1:9061` as a SOCKS proxy and `127.0.0.1:9062` as
  an HTTP proxy. You **must** select the option in the viewer to use the HTTP proxy for all HTTP
  traffic, or logins will fail.
* Optionally, If you want to reduce HTTP proxy lag you can have asset requests bypass the HTTP proxy by setting
  the `no_proxy` env var appropriately. For ex. `no_proxy="asset-cdn.glb.agni.lindenlab.com" ./firestorm`.
* Log in!

### Filtering

By default, the proxy's display filter is configured to ignore many high-frequency messages.
The filter field allows filtering on the presence of specific blocks or the values of 
variables.

For example, to find either chat messages mentioning "foo" or any message referencing `125214`
in an ID field you could use `ChatFrom*.ChatData.Message~="foo" || *.*.*ID==125214`. To find all
ObjectUpdates related to object ID `125214` you could do
`*ObjectUpdate*.ObjectData.*ID==125214 || *ObjectUpdate*.ObjectData.Data.*ID==125214`
to parse through both templated fields and fields inside the binary `Data` fields for compressed and 
terse object updates.

Messages also have metadata attached that can be matched on. To match on all kinds of ObjectUpdates that were
related to the most recently selected object at the time the update was logged, you could do a filter like
`Meta.ObjectUpdateIDs ~= Meta.SelectedLocal`

Similarly, if you have multiple active sessions and are only interested in messages related to a specific
agent's session, you can do `(Meta.AgentID == None || Meta.AgentID == "d929385f-41e3-4a34-a04e-f1fc39f24f12") && ...`.

Vectors can also be compared. This will get any ObjectUpdate variant that occurs within a certain range:
`(*ObjectUpdate*.ObjectData.*Data.Position > (110, 50, 100) && *ObjectUpdate*.ObjectData.*Data.Position < (115, 55, 105))`

If you want to compare against an enum or a flag class in defined in `templates.py`, you can just specify its name:
`ViewerEffect.Effect.Type == ViewerEffectType.EFFECT_BEAM`

### Logging

Decoded messages are displayed in the log pane, clicking one will show the request and
response for HTTP messages, and a human-friendly form for UDP messages. Some messages and
fields have [special packers defined](https://github.com/SaladDais/Hippolyzer/blob/master/hippolyzer/lib/base/templates.py)
that will give a more human-readable form of enum or binary fields, with the original form beside or below it.

For example, an `AgentUpdate` message may show up in the log pane like:

```
OUT AgentUpdate
# 15136: <PacketFlags.ZEROCODED: 128>

[AgentData]
  AgentID = [[AGENT_ID]]
  SessionID = [[SESSION_ID]]
  BodyRotation = (0.0, 0.0, 0.06852579861879349, 0.9976493446715918)
  HeadRotation = (-0.0, -0.0, 0.05799926817417145, 0.998316625570896)
  # Many flag fields are unpacked as tuples with the original value next to them
  State =| ('EDITING',) #16
  CameraCenter = <120.69703674316406, 99.8336181640625, 59.547847747802734>
  CameraAtAxis = <0.9625586271286011, 0.11959066987037659, -0.243267223238945>
  CameraLeftAxis = <-0.12329451739788055, 0.992370069026947, 0.0>
  CameraUpAxis = <0.24141110479831696, 0.029993515461683273, 0.9699592590332031>
  Far = 88.0
  ControlFlags =| ('YAW_POS', 'NUDGE_AT_POS') #524544
  Flags =| ('HIDE_TITLE',) #1
```

and an `ObjectImage` for setting a prim's texture may look like

```
OUT ObjectImage
# 3849: <PacketFlags.0: 0>

[AgentData]
  AgentID = [[AGENT_ID]]
  SessionID = [[SESSION_ID]]
[ObjectData]
  ObjectLocalID = 700966
  MediaURL = b''
  TextureEntry =| {'Textures': {None: '89556747-24cb-43ed-920b-47caed15465f'}, \
     'Color': {None: b'\xff\xff\xff\xff'}, \
     'ScalesS': {None: 1.0}, \
     'ScalesT': {None: 1.0}, \
     'OffsetsS': {None: 0}, \
     'OffsetsT': {None: 0}, \
     'Rotation': {None: 0}, \
     'BasicMaterials': {None: {'Bump': 0, 'FullBright': False, 'Shiny': 'MEDIUM'}}, \
     'MediaFlags': {None: {'WebPage': False, 'TexGen': 'DEFAULT', '_Unused': 0}}, \
     'Glow': {None: 0}, \
     'Materials': {None: '00000000-0000-0000-0000-000000000000'}}
  #TextureEntry = b'\x89UgG$\xcbC\xed\x92\x0bG\xca\xed\x15F_\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x00\x80?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
```

All unpackers also provide equivalent packers that work with the message builder.
The scripting interface uses the same packers as the logging interface, but uses a different
representation. Clicking the "Copy repr()" will give you a version of the message that you can paste into
an addon's script.

### Building Messages

The proxy GUI includes a message builder similar to Alchemy's to allow building arbitrary messages, or
resending messages from the message log window. Both UDP and Caps messages may be sent.

For example, here's a message that will drop a physical cube on your head:

```
OUT ObjectAdd

[AgentData]
  # [[]] in a field value indicates a simple replacement
  # provided by the proxy
  AgentID = [[AGENT_ID]]
  SessionID = [[SESSION_ID]]
  GroupID = [[NULL_KEY]]
[ObjectData]
  # =| means the we should use the field's special packer mode
  # We treat PCode as an enum, so we'll convert from its string name to its int val
  PCode =| 'PRIMITIVE'
  Material = 3
  # With =| you may represent flags as a tuple of strings rather than an int
  # The only allowed flags in ObjectAdd are USE_PHYSICS (1) and CREATE_SELECTED (2)
  AddFlags =| ('USE_PHYSICS',)
  PathCurve = 16
  ProfileCurve = 1
  PathBegin = 0
  PathEnd = 0
  PathScaleX = 100
  PathScaleY = 100
  PathShearX = 0
  PathShearY = 0
  PathTwist = 0
  PathTwistBegin = 0
  PathRadiusOffset = 0
  PathTaperX = 0
  PathTaperY = 0
  PathRevolutions = 0
  PathSkew = 0
  ProfileBegin = 0
  ProfileEnd = 0
  ProfileHollow = 0
  BypassRaycast = 1
  # =$ indicates an eval()ed field, this will result in a vector 3m above the agent.
  RayStart =$ AGENT_POS + Vector3(0, 0, 3)
  # We can reference whatever we put in `RayStart` by accessing `block`
  RayEnd =$ block["RayStart"]
  RayTargetID = [[NULL_KEY]]
  RayEndIsIntersection = 0
  Scale = <0.5, 0.5, 0.5>
  Rotation = <0.0, 0.0, 0.0, 1.0>
  State = 0
```

The repeat spinner at the bottom of the window lets you send a message multiple times.
an `i` variable is put into the eval context and can be used to vary messages across repeats.
With repeat set to two:

```
OUT ChatFromViewer

[AgentData]
  AgentID = [[AGENT_ID]]
  SessionID = [[SESSION_ID]]
[ChatData]
  # Simple templated f-string
  Message =$ f'foo {i * 2}'
  Type =| 'NORMAL'
  Channel = 0
```

will print

```
User: foo 0
User: foo 2
User: foo 4
```

HTTP requests may be sent through the same window, with equivalent syntax for replacements
and `eval()` within the request body, if requested. As an example, sending a chat message
through the `UntrustedSimulatorMessage` cap would look like:

```
POST [[UntrustedSimulatorMessage]] HTTP/1.1
Content-Type: application/llsd+xml
Accept: application/llsd+xml
X-Hippo-Directives: 1

<llsd>
<map>
   <key>message</key>
    <string>ChatFromViewer</string>
   <key>body</key>
    <map>
     <key>AgentData</key>
      <array>
        <map>
         <key>AgentID</key>
          <uuid><!HIPPOREPL[[AGENT_ID]]></uuid>
         <key>SessionID</key>
          <uuid><!HIPPOREPL[[SESSION_ID]]></uuid>
        </map>
      </array>
     <key>ChatData</key>
      <array>
        <map>
         <key>Channel</key>
          <integer>0</integer>
         <key>Message</key>
          <string>test <!HIPPOEVAL[[
            base64.b64encode(hex(1 + 1).encode("utf8"))
          ]]></string>
         <key>Type</key>
          <integer>1</integer>
        </map>
      </array>
    </map>
  </map>
</llsd>
```

## Addon commands

By default, channel 524 is a special channel used for commands handled by addons'
`handle_command` hooks. For ex, an addon that supplies a `foo` with one string parameter
can be called by typing `/524 foo something` in chat.

`/524 help` will give you a list of all commands offered by currently loaded addons.

## Useful Extensions

These are quick and dirty, but should be viewer features. I'm not a viewer developer, so they're here. 
If you are a viewer developer, please put them in a viewer.

* Local Animation - Allows loading and playing animations in LL's internal format from disk, replaying
  when the animation changes on disk. Mostly useful for animators that want quick feedback
* Local Mesh - Allows specifying a target object to apply a mesh preview to. When a local mesh target
  is specified, hitting the "calculate upload cost" button in the mesh uploader will instead
  apply the mesh to the local mesh target. It works on attachments too. Useful for testing rigs before a 
  final, real upload.

## Potential Changes

* AISv3 wrapper?
* Higher level wrappers for common things? I don't really need these, so only if people want to write them.
* Move things out of `templates.py`, right now most binary serialization stuff lives there
  because it's more convenient for me to hot-reload.
* Ability to add menus?

## License

[LGPLv3](https://www.gnu.org/licenses/lgpl-3.0.en.html). If you have a good reason why, I might dual license.

This package [includes portions of the Second Life(TM) Viewer Artwork](https://github.com/SaladDais/Hippolyzer/tree/master/hippolyzer/lib/base/data),
Copyright (C) 2008 Linden Research, Inc.  The viewer artwork is licensed under the Creative Commons
Attribution-Share Alike 3.0 License.

## Contributing

Ensure that any patches are clean with no unnecessary whitespace or formatting changes, and that you
add new tests for any added functionality.

## Philosophy

With a few notable exceptions, Hippolyzer focuses mainly on decomposition of data, and doesn't
provide many high-level abstractions for interpreting or manipulating that data. It's careful
to only do lossless transforms on data that are just prettier representations of the data sent
over the wire. Hippolyzer's goal is to help people understand how Second Life actually works,
automatically employing abstractions that hide how SL works is counter to that goal.

## For Client Developers

This section is mostly useful if you're developing a new SL-compatible client from scratch. Clients based
on LL's will work out of the box.

### Adding proxy support to a new client

Hippolyzer's proxy application actually combines two proxies, a [SOCKS 5](https://tools.ietf.org/html/rfc1928)
UDP proxy and an HTTP proxy.

To have your client's traffic proxied through Hippolyzer the general flow is:

* Open a TCP connection to Hippolyzer's SOCKS 5 proxy port
* * This should be done once per logical user session, as Hippolyzer assumes a 1:1 mapping of SOCKS TCP 
    connections to SL sessions
* Send a UDP associate command without authentication
* The proxy will respond with a host / port pair that UDP messages may be sent through
* At this point you will no longer need to use the TCP connection, but it must be kept
  alive until you want to break the UDP association
* Whenever you send a UDP packet to a remote host, you'll need to instead send it to the host / port
  from the UDP associate response. A SOCKS 5 header must be prepended to the data indicating the ultimate destination
  of the packet
* Any received UDP packets will also have a SOCKS 5 header indicating the real source IP and address
* * When in doubt, check `socks_proxy.py`, `packets.py` and the SOCKS 5 RFC for more info on how to deal with SOCKS.
* * <https://github.com/SaladDais/WinHippoAutoProxy/blob/master/winhippoautoproxy/socks5udphooker.cpp> is a simple
    example that wraps around `recvfrom()` and `sendto()` and could be used as a starting point.
* All HTTP requests must be sent through the Hippolyzer's HTTP proxy port.
* * You may not need to do any extra plumbing to get this to work if your chosen HTTP client
    respects the `HTTP_PROXY` environment variable.
* All HTTPS connections will be encrypted with the proxy's TLS key. You'll need to either add it to whatever
  CA bundle your client uses or disable certificate validation when a proxy is used.
* * mitmproxy does its own certificate validation so disabling it in your client is OK.
* The proxy needs to use content sniffing to figure out which requests are login requests,
  so make sure your request would pass `MITMProxyEventManager._is_login_request()`

### Should I use this library to make an SL client in Python?

No. If you just want to write a client in Python, you should instead look at using 
[libremetaverse](https://github.com/cinderblocks/libremetaverse/) via pythonnet.
I removed the client-related code inherited from PyOGP because libremetaverse's was simply better.

<https://github.com/CasperTech/node-metaverse/> also looks like a good, modern wrapper if you
prefer TypeScript.
