#!/usr/bin/python
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
