#!/usr/bin/python

bag = {}
props = {}
params = {}

bag_stack = []
props_stack = []
params_stack = []

def push():
  global bag,props,params
  global bag_stack,props_stack,params_stack

  bag_stack.append(bag)
  props_stack.append(props)
  params_stack.append(params)
  bag = {}
  props = {}
  params = {}

def pop():
  global bag,props,params
  global bag_stack,props_stack,params_stack
 
  bag = bag_stack[-1]
  props = props_stack[-1]
  params = params_stack[-1]

  bag_stack = bag_stack[:-1]
  props_stack = props_stack[:-1]
  params_stack = params_stack[:-1]
