#include "main.h"

void rename(string a, string b, SList *l){
    if(l->m_atom == a)
      l->m_atom = b;
    for(auto it=l->m_list.begin(); it!=l->m_list.end(); it++)
       if(*it)
          rename(a,b,*it);
}

void renames(string a, string b, SList *l, void(*lambda)(SList*)){
    if(l->m_atom.rfind(a,0) == 0){
      l->m_atom = b;
      if(lambda)
        (*lambda)(l);
    }
    for(auto it=l->m_list.begin(); it!=l->m_list.end(); it++)
       if(*it)
          renames(a,b,*it,lambda);
}


void rpn(string a, SList *l){
    if(l->m_atom == a && l->m_list.size()){
      l->m_atom = "";
      vector<SList*> new_list;
      new_list.push_back(l->m_list.front());
      for(auto it=next(l->m_list.begin(),1); it!=l->m_list.end(); it++){
          new_list.push_back(new SList(0,a));
          new_list.push_back(*it);
      }
      l->m_list = new_list;
    }
    for(auto it=l->m_list.begin(); it!=l->m_list.end(); it++)
       if(*it)
          rpn(a,*it);
}

void mov_inside(string a, SList *l){
    if(l->m_atom == a && l->m_list.size()){
      l->m_atom = "";
      vector<SList*> new_list;
      new_list.push_back(l->m_list.front());
      new_list.push_back(new SList(0,a));
      l->m_list = new_list;
    }
    for(auto it=l->m_list.begin(); it!=l->m_list.end(); it++)
       if(*it)
          mov_inside(a,*it);
}

void rot_back(string a, SList **pl){
    SList *l = *pl;
    if(l->m_atom == a){
       SList *nl = l->m_list[0];
       nl->m_list.push_back(l);
       l->m_list.erase(l->m_list.begin());
       l->m_atom = "";
       l->m_noparen=true;
       *pl = nl;
       l=nl;
    }
    for(auto it=l->m_list.begin(); it!=l->m_list.end(); it++)
       if(*it)
          rot_back(a,&(*it));

}

