
class Avatar(object):
    """an avatar - the agent representation in 3D on a region"""
    
    def __init__(self, region):
        """initialize the avatar with the actual region we are on
        
        we need to instantiate the avatar after place_avatar
        """
        self.region = region