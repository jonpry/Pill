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

import klayout.db as db


def Path(dpts,width,justification):
   path = db.DPath.new()
   path.width = width

   ds=[]
   for i in range(len(dpts)-1):
      apt = dpts[i]
      bpt = dpts[i+1]
      if bpt.x > apt.x:
        d = 'R'
      elif bpt.y > apt.y:
        d = 'U'
      elif bpt.x < apt.x:
        d = 'L'
      elif bpt.y < apt.y:
        d = 'D'
      else:
        assert(False)
      ds.append(d)
   delta = 0
   if justification == "right":
     delta = +width/2
   elif justification == "left":
     delta = -width/2
   elif justification == "center":
     pass
   else:
     assert(False)

   for i in range(len(dpts)-1):
      if ds[i] == "R":
        dpts[i].y += delta         
        dpts[i+1].y += delta         
      elif ds[i] == "L":
        dpts[i].y -= delta         
        dpts[i+1].y -= delta         
      elif ds[i] == "U":
        dpts[i].x -= delta         
        dpts[i+1].x -= delta         
      elif ds[i] == "D":
        dpts[i].x += delta         
        dpts[i+1].x += delta         

   path.points = dpts
   return path

#dpts = [db.DPoint.new(0,0),db.DPoint.new(0,1)]  
#p = Path(dpts,0.050,"right")
#print p
