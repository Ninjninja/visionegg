"""Trace calls to OpenGL

With this module, you can trace all calls made to OpenGL through PyOpenGL.
To do this, substitute

import OpenGL.GL as gl

with

import VisionEgg.GLTrace as gl

in your code.

Also, trace another module's use of OpenGL by changing its reference
to OpenGL.GL to a reference to VisionEgg.GLTrace.

This module also imports everything in OpenGL.GL.ARB.multitexture.
"""

# Copyright (c) 2003 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import OpenGL.GL as gl

import OpenGL.GL.ARB.multitexture
for attr in dir(OpenGL.GL.ARB.multitexture):
    # put attributes from multitexture module in "gl" module dictionary
    # (Namespace overlap as you'd get OpenGL apps written in C)
    if attr[0:2] != "__":
        setattr(gl,attr,getattr(OpenGL.GL.ARB.multitexture,attr))

import string        
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

gl_constants = {}

# functions which we don't want to map all the arguments of
special_functions = {'glTexImage2D':[1,3,4,5], # level,width,height,border
                     }

def arg_to_str( arg ):
    if type(arg) == int:
        if arg in gl_constants.keys():
            return gl_constants[arg]
    elif type(arg) == str:
        return "'<string>'"
    return repr(arg)

class Wrapper:
    def __init__(self, attr_name):
        self.attr_name = attr_name
        self.orig_func = getattr(gl,self.attr_name)
    def run(self,*args,**kw):
        if kw: kw_str = " AND KEYWORDS"
        else: kw_str = ""
        if self.attr_name in special_functions:
            arg_str = []
            for i in range(len(args)):
                if i in special_functions[self.attr_name]:
                    arg_str.append(str(args[i])) # don't convert to name of OpenGL constant
                else:
                    arg_str.append(arg_to_str(args[i])) # convert to name of OpenGL constant
            arg_str = string.join( arg_str, "," )
        else:
            arg_str = string.join( map( arg_to_str, args ), "," )
        print "%s(%s)%s"%(self.attr_name,arg_str,kw_str)
        result = self.orig_func(*args,**kw)
        return result

for attr in dir(gl):
    if callable( getattr(gl,attr) ):
        wrapper = Wrapper(attr)
        cmd = "%s = wrapper.run"%attr
        exec cmd
    else:
        cmd = "%s = getattr(gl,'%s')"%(attr,attr)
        exec cmd
        if attr[:2] != '__' and attr[-2:] != '__':
            if type(getattr(gl,attr)) == int:
                if getattr(gl,attr) > 256: # assume first n aren't constants (n is arbitrary choice)
                    gl_constants[getattr(gl,attr)] = attr
        
