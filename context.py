#!/usr/bin/python

#Copyright (C) 2019 Jon Pry
#
#This file is part of Pill.
#
#Pill is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 2 of the License, or
#(at your option) any later version.
#
#Pill is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with Pill.  If not, see <http://www.gnu.org/licenses/>.


bag = {}
props = {}
params = {}
shapes = []

bag_stack = []
props_stack = []
params_stack = []
shapes_stack = []

def push():
  global bag,props,params,shapes
  global bag_stack,props_stack,params_stack,shapes_stack

  bag_stack.append(bag)
  props_stack.append(props)
  params_stack.append(params)
  shapes_stack.append(shapes)
  bag = {}
  props = {}
  params = {}
  shapes = []

def pop():
  global bag,props,params,shapes
  global bag_stack,props_stack,params_stack,shapes_stack
 
  bag = bag_stack[-1]
  props = props_stack[-1]
  params = params_stack[-1]
  shapes = shapes_stack[-1]

  bag_stack = bag_stack[:-1]
  props_stack = props_stack[:-1]
  params_stack = params_stack[:-1]
  shapes_stack = shapes_stack[:-1]
