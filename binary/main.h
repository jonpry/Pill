#pragma once

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>

#include <vector>
#include <map>
#include <set>
#include <algorithm>

using namespace std;

class SList;

extern set<uint64_t> consumed;

class SList {
 public:
   SList(uint64_t ofst, string atom="", vector<SList*> *slist=0){
      m_atom = atom;
      m_ofst = ofst;
      if(slist){
         m_list = *slist;  
         for(auto it=m_list.begin(); it!=m_list.end(); it++){
            if(*it)
               consumed.insert((*it)->m_ofst);
         }
      }
   }

   void print(){
     printf("%s", m_atom.c_str());
     if(m_list.size())
        printf("(");
     for(auto it=m_list.begin(); it!=m_list.end(); it++){
        if(*it)
           (*it)->print();
        else
           printf("NULLPTR!!!!");
        printf(" ");
     }
     if(m_list.size())
        printf(")");
   }

   uint64_t m_ofst;
   string m_atom;
   vector<SList*> m_list;
};
