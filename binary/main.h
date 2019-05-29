#pragma once

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>

#include <vector>
#include <map>

using namespace std;

class SList {
 public:
   SList(string atom="", vector<SList*> *slist=0){
      m_atom = atom;
      if(slist)
         m_list = *slist;  
   }

   void print(){
     printf("%s", m_atom.c_str());
     if(m_list.size())
        printf("(");
     for(auto it=m_list.begin(); it!=m_list.end(); it++){
        (*it)->print();
        printf(" ");
     }
     if(m_list.size())
        printf(")");
   }

   string m_atom;
   vector<SList*> m_list;
};
