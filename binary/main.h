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
#include <sstream>

using namespace std;

class SList;

extern set<uint64_t> consumed;

void print_token(string s);
void print_reset();

template <typename T>
string to_scientific(const T a_value, const int n = 11)
{
    ostringstream out;
    out.precision(n);
    out << scientific << a_value;
    return out.str();
}

class SList {
 public:
   SList(uint64_t ofst, string atom="", vector<SList*> *slist=0){
      m_atom = atom;
      assert(m_atom.size());
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
     if(m_atom.size())
        print_token(m_atom);
     if(m_list.size())
        print_token("(");
     else 
        assert(m_atom.size());
     for(auto it=m_list.begin(); it!=m_list.end(); it++){
        if(*it)
           (*it)->print();
        else
           print_token("NULLPTR!!!!");
     }
     if(m_list.size())
        print_token(")");
   }

   uint64_t m_ofst;
   string m_atom;
   vector<SList*> m_list;
};

class Func {
 public:
   Func(uint32_t len, uint32_t n_args) : m_len(len), m_args(n_args) {}

   uint32_t m_len, m_args;
};
