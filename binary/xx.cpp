//Copyright (C) 2019 Jon Pry
//
//This file is part of Pill.
//
//Pill is free software: you can redistribute it and/or modify
//it under the terms of the GNU General Public License as published by
//the Free Software Foundation, either version 2 of the License, or
//(at your option) any later version.
//
//Pill is distributed in the hope that it will be useful,
//but WITHOUT ANY WARRANTY; without even the implied warranty of
//MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//GNU General Public License for more details.
//
//You should have received a copy of the GNU General Public License
//along with Pill.  If not, see <http://www.gnu.org/licenses/>.

#include "main.h"

set<uint64_t> consumed;
map<uint64_t,SList*> frompos;

const char *types[] = { "0", "char", "short", "int", 
                        "long", "float", "double", "pointer",
                        "byte", "car", "cdr", "LPType", 
                        "MX", "MXR90", "MY", "MYR90", 
                        
                        "PCB", "XXString", "XXfreeObject", "XXfreeObject2", 
                        "XXgroup", "XXgroupMember", "XXilList", "XXilSymbol", 
                        "XXparentChild", "XXpropVal", "XXproperty", "XXrange", 
                        "XXrcb", "aBoolean", "aDouble", "aFileName", 

                        "aFloat", "aIlExpr", "aInt", "aNetSet",
                        "aNlpExpr", "aProperty", "aRange", "aSelfIdent", 
                        "aString", "aTime", "accessDir", "ailList", 
                        "analog", "arc", "arcType", "ascOwnrType", 

                        "assocOwner", "assocOwnerUnion", "assocType", "assocUnion", 
                        "associate", "attrAssocType", "attrOwner", "bBox", 
                        "bbox", "beginExt", "behavioral", "bytes", 
                        "cellName", "cellViewType", "child", "clock", 

                        "columnBiasedMos", "columnOffset", "columnSpacing", "columns", 
                        "connStatus", "connectOutside", "connected", "contraints", 
                        "criticality", "dataFileId", "dbBBox", "dbPoint", 
                        "defValue", "delta",  "deltaX", "deltaY", 

                        "deltas", "direction", "displayFlags", "donut", 
                        "donutType", "dot", "dotType", "dummy1", 
                        "dummy2", "dummy3", "dummyType1", "dummyType2", 
                        "dummyType3", "dummyType4", "dummyType5", "dummyType6", 

                        "dummyType7", "edgeConnected", "ellipse", "ellipseType", 
                        "emptyMosaic", "endExt", "extendExtend", "fig", 
                        "firm", "flags", "freeArray", "freeArraySize", 
                        "graphic", "ground", "group", "groupMemType", 

                        "groupType", "headerRef", "height", "hole", 
                        "icon", "index", "input", "inputOutput", 
                        "inst", "instHeader", "instHeaderType", "instInfo", 
                        "instPin", "instPinType", "instPinUnion", "instTerm", 

                        "instTermType", "instTermUnion", "instType", "instanceList", 
                        "instances", "instsBBox", "isGlobal", "isStart1", 
                        "isStart2", "jumper", "lBound", "label",
                        "labelAssocType", "labelType", "largeNetNumBits", "largeSigArray", 

                        "lastInGroup", "lastSigArySize", "layer", "libName", 
                        "line", "lineType", "locked", "logicModel",
                        "lowerLeft", "mag", "magInst", "magInstInfo", 
                        "manh2line", "manh2path", "maskLayout", "masterAttr", 
//160
                        "masterBBox", "masterMemRcb", "masterProp", "masterTermAttr", 
                        "masterTermProp", "maxExtension", "memNet", "members", 
                        "memoryRcb", "modifiedButNotSaved", "mosaic", "mosaicInstType",
                        "mosaicTileType", "mosaicType", "nPoints", "nShapes",

                         "name", "nameNumber", "nameString", "needToConnect",
                         "net", "netFig", "netType", "netUnion", 
                         "netlist", "next", "nextFree", "nextGroup", 
                         "nextGroupForObject", "nextInAssoc", "nextInGroup", "nextInObj1", 
//192
                         "nextInObj2", "nextInOwner", "nextInView", "nextOnInst", 
                         "nextOnInstTerm", "nextOnNet", "nextOnTerm", "numBits", 
                         "numInst", "numInstTypes", "numInstances", "numMemNet", 
                         "obj1", "obj2", "object", "offset",
//208
                         "ofjbtd", "oldInst", "orient", "output", 
                         "owner", "pLPAnnex", "package", "pad", 
                         "padSpace1", "padSpace2", "padSpace3", "padSpace4", 
                         "pair", "paramAssocType", "parent", "path", 

                         "pathType", "personality", "pin", "pinType", 
                         "pinUnion", "placeInfo", "placeStatus", "placed", 
                         "point0", "points", "polygon", "polygonType", 
                         "prefixChar", "prop", "propAssocType", "propType", 
//240
                         "purpose", "quad", "r0", "r180", 
                         "r270", "r90", "rcb", "readInFlag", 
                         "rect", "rectType", "regularMosaic", "roundRound",
                         "rowBiasedMosaic", "rowOffset", "rowSpacing", "rows",
 
                         "sBounds", "schematic", "schematicSymbol", "shape",
                         "sibling", "sigArray", "sigType", "signal", 
                         "simpleMosaic", "startAngle", "stranger", "style", 
                         "subInfo", "subInst", "suggested", "supply", 
//272
                         "sweepAngle", "switch", "symbolic", "term", 
                         "termType", "termUnion", "testLatch", "text", 
                         "textDisplay", "textDisplayType", "theLabel", "timeStamp", 
                         "truncateExtend", "type", "uBound", "uX", 
    
                         "uY", "uint1D", "unknown", "unplaced", 
                         "unused", "unused2", "unused3", "upperRight", 
                         "usedIn", "value", "valueType", "varExtendExtend", 
                         "variants", "verilogMap", "view", "viewName", 
//304
                         "vofbtdP", "vofjtdP", "width", "x",
                         "xy", "y", "yFirst", "ze2OldMosaic", 
                         "zeAnyInst", "zeAnyInstName", "zeArc", "zeCellView", 
                         "zeDonut", "zeFig", "zeFigPar", "zeInst", 
//320
                         "zeInstHeader", "zeInstInfo", "zeInstName", "zeInstPin", 
                         "zeInstTerm", "zeLP", "zeLabel", "zeLine", 
                         "zeLrgSigAryInfo", "zeMagInst", "zeMagInstInfo", "zeMosaic", 
                         "zeMosaicTile", "zeNet", "zeNetFigUnion", "zeOldFig", 

                         "zeOldInstHeader", "zeOldMosaic", "zeOldNetFig", "zeOldTextDisplay", 
                         "zeOrthPolygon", "zePath", "zePhysConn", "zePin", 
                         "zePinFigUnion", "zePlacementInfo", "zePolygon", "zeSig", 
                         "zeTerm", "zeTextDisplay", "zeUX", "zeUX2", 
//352
                         "zeUY", "zeUY2", "zeUnionX", "zeUnionY", 
                         "zebBox", "zeoldFigPar", "zeoldsubInfo", "zeoldsubInst", 
                         "zesubinfo", "zesubInst"}; 
/*  Sizes64
Type Name		Type Id		Size in bytes
----------		--------	-------------
char            	     0			 1
char            	     1			 1
short           	     2			 2
short           	     3			 2
int             	     4			 4
int             	     5			 4
long            	     6			 8
long            	     7			 8
float           	     8			 4
float           	     9			 4
double          	    10			 8
double          	    11			 8
pointer         	    12			 8
pointer         	    13			 8
byte            	    14			 1
byte            	    15			 1
XXrcb           	    16			48
XXfreeObject2   	    18			 8
XXfreeObject    	    19			16
XXproperty      	    20			40
XXrange         	    21			32
XXgroup         	    22			32
XXgroupMember   	    23			40
XXilSymbol      	    32			 8
XXilList        	    33			16
dbPoint         	    34			 8
dbPoint         	    35			 8
dbBBox          	    36			16
dbBBox          	    37			16
XXparentChild   	    38			16
XXSstring       	    40			 4
zeCellView      	    50			88
zeOldInstHeader 	    51			104
zeLP            	    52			40
zeOldFig        	    60			48
zeInst          	    61			40
ze2OldMosaic    	    62			72
zeMosaicTile    	    63			 2
zeMosaicTile    	    64			 2
zeLabel         	    65			32
zeArc           	    66			40
zeDonut         	    67			16
zePolygon       	    68			12
zeOrthPolygon   	    69			16
zeLine          	    71			12
zePath          	    74			24
zeNet           	    80			64
zeSig           	    81			32
zeTerm          	    82			40
zePin           	    83			40
zeInstTerm      	    84			40
zeInstPin       	    85			24
zeOldNetFig     	    86			16
zePhysConn      	    87			40
zeOldMosaic     	    88			72
zeFig           	    89			56
zeOldTextDisplay	    90			48
zeTextDisplay   	    91			80
zeInstHeader    	    92			104
zeMosaic        	    93			72
zeAnyInst       	    94			56
zeMagInst       	    95			16
zeLrgSigAryInfo 	    96			 8
*/

uint32_t sizes32[] = { 1, 1, 2, 2, 4, 4, 4, 4, 
                     4, 4, 8, 8, 4, 4, 1, 1, 
                     0x24, 0, 4, 0xc, 0x14, 0x10, 0x10, 0x14, 
                     0, 0, 0, 0, 0, 0, 0, 0,
                     4, 8, 8, 8, 0x10, 0x10, 8, 0,
                     4, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0x24, 0x44, 0x1c, 0, 0, 0,
                     0, 0, 0, 0, 0x20, 0x1c, 0x30, 2,
                     2, 0x14, 0x28, 0x10, 0xc, 0x10, 0, 0xc,
                     0, 0, 0x18, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0x20, 0x10, 0x14, 0x14,
                     0x14, 0xc, 8, 0x14, 0x30, 0x20, 0x1c, 0x2c,
                     0x44, 0x30, 0x20, 8};


uint32_t sizesc32[] = { 4, 1, 4, 2, 4, 4, 4, 4,  //0
                     4, 4, 8, 8, 4, 4, 1, 1,  //0x8
                     0x24, 0, 4, 0x8, 0xe, 0x10, 0x9, 0x10, //0x10 
                     0, 0, 0, 0, 0, 0, 0, 0, //0x18
                     4, 8, 8, 8, 0x10, 0x10, 8, 0, //0x20
                     4, 0, 0, 0, 0, 0, 0, 0, //0x28
                     0, 0, 0x110-0xe8-4, 0x44, 0xe, 0, 0, 0, //0x30
                     0, 0, 0, 0, 0x20, 0x1c, 0x30, 2, //0x38
                     2, 0x14, 0x28, 0x10, 0xc, 0x10, 0, 0x1c, //0x40
                     0, 0, 0x18, 0, 0, 0, 0, 0, //0x48
                     0x1a7, 8, 40, 40, 0x20, 0x10, 0x14, 0x14, //0x50
                     0x14, 0xc, 8, 0x14, 0x30, 0x20, 0x1a, 0x2c,//0x58
                     0x44, 0x30, 0x20, 8};

uint32_t stringidx[] = {1, 1, 2, 2, 3, 3, 4, 4, //0
                        5, 5, 6, 6, 7, 7, 8, 8, //0x8
                        0x1c, 0, 0x13, 0x12, 0x1a, 0x1b, 0x14, 0x15, //0x10
                        0, 0, 0, 0, 0, 0, 0, 0, //0x18
                        0x17, 0x16, 0x4B, 0x4B, 0x4A, 0x4A, 0x18, 0,  //0x20
                        0x11, 0, 0, 0, 0, 0, 0, 0, //0x28
                        0, 0, 315, 0x150, 0x145, 0, 0, 0, //0x30
                        0, 0, 0, 0, 0x14f, 0x13f, 0x137, 0x14c, //0x38
                        0x14c, 0x146, 0x13a, 0x13c, 0x15a, 0x154, 0, 0x147, //0x40 
                        0, 0, 0x155, 0, 0, 0, 0, 0, //0x48
                        0x14d, 0x15b, 0x15c, 0x157, 0x144, 0x143, 0x152, 0x156, //0x50, 
                        0x151, 0x13d, 0x153, 0x15d, 0x140, 0x14b, 0x138, 0x149,
                        0x148, 0, 0, 0}; 

set<uint32_t> arrayTypes = {1,3,5,7,9,11,13,15,35,37,64};

string prop_types[] = { "uknown", "string", "int", "float", "bool", "time", "file", "expr", "nexpr", "hier", "list", "net"};

#define MIN(a,b) ((a)<(b)?(a):(b))

void printbytes(uint8_t *buf, uint32_t len){
   for(uint32_t i=0; i < len; i+=16){
      printf("%4.4X: ", i);
      for(uint32_t j=i; j < MIN(i+16,len); j++){
         printf("%2.2X ", buf[j]);
      }
      printf("\n");
   }
}

void parseseg(uint8_t* buf, uint32_t seg_start, uint32_t pos, uint32_t i, uint32_t b){
       #if 1

       //Some kind of element header
       //if(i==0)
       while(b>0){
       uint32_t type = __bswap_16(*(uint16_t*)&buf[pos+2]) & 0xFF; 
       if(type>96 || !stringidx[type])
          return;

       uint32_t esz = sizes32[type];
 
       uint32_t nelem=1; //if !arrayType

       uint32_t rel_pos = ((i+1)<<16) + pos-seg_start - 0x40 + 0x4 + 1;
       printf("El Type: %x %dd,%s, TS: %d@%lx:%lx  %x\n", type, type, types[stringidx[type]], esz, rel_pos+(type==1?8:0),pos, __bswap_32(*(uint32_t*)&buf[pos]));
       assert(*(uint16_t*)&buf[pos] == 0);

       //assert(typeMap.find(type) != typeMap.end());

       pos+=0x4;
       b-=0x4;

       if(arrayTypes.find(type)!=arrayTypes.end()){
          esz = __bswap_32(*(uint32_t*)&buf[pos]) - 4;
          rel_pos+=8;
          if(type==1){ //string
             printf("String: %x %s\n", esz, &buf[pos+8]);
             new SList(rel_pos,"\"" + string((char*)&buf[pos+8]) + "\"");
          }
       }

       if(type==32){
            uint32_t aloc = __bswap_32(*(uint32_t*)&buf[pos]) &0xFFFFF;
            printf("Aloc: %X\n", aloc);
            vector<SList*> args;
            if(aloc)
               args.push_back(new SList(true,aloc));
            new SList(rel_pos,"symbol",&args);
       }

       if(type==4){
            int32_t aloc = __bswap_32(*(int32_t*)&buf[pos]);
            new SList(rel_pos,to_string(aloc));
       }

       if(type==0){
            int8_t aloc = *(int8_t*)&buf[pos];
            new SList(rel_pos,to_string(aloc));
       }

       if(type==10){
            uint64_t aloc = __bswap_64(*(uint64_t*)&buf[pos]);
            double d = *(double*)&aloc;
            new SList(rel_pos,format_double(d));
       }

       if(type==19){
            uint32_t aloc = __bswap_32(*(uint32_t*)&buf[pos]);
            esz += __bswap_32(*(uint32_t*)&buf[pos+4])*4;
            printf("Aloc: %X\n", aloc);
            vector<SList*> args;
            if(aloc)
               args.push_back(new SList(true,aloc));
            new SList(rel_pos,"freeObject",&args);
       }
     

       if(type==20){
            uint32_t aloc = __bswap_32(*(uint32_t*)&buf[pos]);
            uint32_t bloc = __bswap_32(*(uint32_t*)&buf[pos+0xc]);
            uint32_t cloc = __bswap_32(*(uint32_t*)&buf[pos+0x10]);
            printf("Aloc: %X %X %X\n", aloc, bloc, cloc);
            vector<SList*> args;
            if(aloc)
               args.push_back(new SList(true,aloc));
            if(bloc && !(bloc>>24))
               args.push_back(new SList(true, bloc));
            if(cloc)
               args.push_back(new SList(true, cloc));
            new SList(rel_pos,"property",&args);
        }

        if(type==33){
            uint32_t aloc = __bswap_32(*(uint32_t*)&buf[pos]);
            uint32_t bloc = __bswap_32(*(uint32_t*)&buf[pos+4]);
            printf("Aloc: %X %X\n", aloc, bloc);
            vector<SList*> args;
            if(aloc)
               args.push_back(new SList(true,aloc));
            if(bloc)
               args.push_back(new SList(true, bloc));
            new SList(rel_pos,"list",&args);
        }
 
        if(frompos.find(rel_pos) == frompos.end()){
            new SList(rel_pos,string("unknown_") + types[stringidx[type]]);
        }

        printbytes(&buf[pos], esz);

        pos+=esz;
        b-=esz;
     }
}

SList* consume_pointer(uint32_t *pos, int32_t *b, uint8_t *buf, bool force=false, uint32_t *rel_pos=0){
   SList *ret=0;
   if(buf[(*pos)+1] || force){
      uint32_t aloc = __bswap_32(*(uint32_t*)&buf[*pos]);
      *pos+=4;
      *b-=4;
      ret = new SList(true,aloc);
   }else{
      *pos+=2;
      *b-=2;
      ret = new SList(0,"nil");
   }

   if(rel_pos){
     *rel_pos += 4;
   }

   return ret;
}

SList* consume_u32(uint32_t *pos, int32_t *b, uint8_t *buf){
   uint32_t aloc = __bswap_32(*(uint32_t*)&buf[*pos]);
   *pos+=4;
   *b-=4;
   return new SList(0,"0x" + to_hex(aloc));
}


SList* consume_byte(uint32_t *pos, int32_t *b, uint8_t *buf){
   *pos+=1;
   *b-=1;
   return new SList(0,string("byte_") + to_string(buf[*pos-1]));
}


void parsecseg(uint8_t* buf, uint32_t seg_start, uint32_t pos, uint32_t i, int32_t b, const char* fname){
       //Some kind of element header
       //if(i==0)
   uint32_t rel_pos = ((i+1)<<16)+1;
   uint32_t cnt=0;
   while(b>0){
       vector<SList*> args;
       uint32_t opos=pos;

       uint32_t type = buf[pos]; 
       if(type>96 || !stringidx[type]){
          printf("Bad type %x %d\n", type, type);
          //exit(0);
          assert(false);
          return;
       }

       uint32_t esz = sizesc32[type];
 
       uint32_t nelem=1; //if !arrayType
 
       if(cnt++ == 2 && i == 0)
          rel_pos += 0x38;
       rel_pos+=4;

       printf("El Type: %x,%s, TS: %d@%lx:%lx  %x in %s\n", type, types[stringidx[type]], esz, (type==0x1?8:0)+rel_pos,pos, __bswap_32(*(uint32_t*)&buf[pos]), fname);

       //assert(typeMap.find(type) != typeMap.end());

       pos+=0x1;
       b-=0x1;
       int32_t extra=0;
   
       if(type==37){ //dbbox array
           esz=0;
           args.push_back(consume_pointer(&pos,&b,buf));
       }else if(arrayTypes.find(type)!=arrayTypes.end()){
          esz = __bswap_16(*(uint16_t*)&buf[pos]) - 12;
          pos+=2;
          b-=2;

          if(type==0xd){ 
             for(uint32_t i=0; i < esz/4; i++)
                args.push_back(consume_pointer(&pos,&b,buf));
          }else{
             if(type==1){ //string
                printf("String: %dd %s\n", esz, &buf[pos]);
                new SList(rel_pos+8,"\"" + string((char*)&buf[pos]) + "\"");
             }
             pos+=esz;
             b-=esz;
          }
          if(__bswap_16(*(uint16_t*)&buf[opos+1])-4 > 0xC)
             rel_pos+=__bswap_16(*(uint16_t*)&buf[opos+1])-4;
          else
             rel_pos+=0xc;
          //rel_pos+=esz+8;
          esz=0;
          printbytes(&buf[opos], esz+(pos-opos));
          continue;
      }else if(type==0){ //char
            int8_t aloc = *(int8_t*)&buf[pos];
            esz=1;
            new SList(rel_pos,to_string(aloc));
       }else if(type==4){ //int
            int32_t aloc = __bswap_32(*(int32_t*)&buf[pos]);
            new SList(rel_pos,to_string(aloc));
       }else if(type==10){ //double
            uint64_t aloc = __bswap_64(*(uint64_t*)&buf[pos]);
            double d = *(double*)&aloc;
            printf("D: %lX\n", aloc);
            new SList(rel_pos,format_double(d));
       }else if(type==12){ //pointer
           esz=0;
           args.push_back(consume_pointer(&pos,&b,buf,true));
       }else if(type==16){//rcb
           esz=0;
           args.push_back(consume_u32(&pos,&b,buf));
           args.push_back(consume_pointer(&pos,&b,buf,true));
           args.push_back(consume_byte(&pos,&b,buf));
           args.push_back(consume_byte(&pos,&b,buf));
           args.push_back(consume_u32(&pos,&b,buf));
           args.push_back(consume_u32(&pos,&b,buf));
           args.push_back(consume_u32(&pos,&b,buf));
           args.push_back(consume_u32(&pos,&b,buf));
           args.push_back(consume_u32(&pos,&b,buf)); //This may be a pointer past the end
           args.push_back(consume_pointer(&pos,&b,buf));
           args.push_back(consume_pointer(&pos,&b,buf,true));
            new SList(rel_pos,"rcb",&args);
       }else if(type==18){
           esz=0;
       }else if(type==19){ //freeobject
           esz=4;
           extra=4;
           uint32_t free = __bswap_32(*(uint32_t*)&buf[pos]);
           extra += 4 * free;
       }else if(type==20){ //property
            esz=0;
            uint32_t orel_pos = rel_pos;
            args.push_back(consume_pointer(&pos,&b,buf,true));
            uint8_t ptype = buf[pos++];
            b-=1;
            args.push_back(new SList(0,string("type_") + to_hex(ptype)));
            args.push_back(consume_byte(&pos,&b,buf));
            if(ptype==0xa){
               args.push_back(consume_pointer(&pos,&b,buf,true));
               //extra+=3;
            }else{
               if(ptype==0 || ptype == 0xd)
                  args.push_back(consume_pointer(&pos,&b,buf,true));
               else
                  args.push_back(consume_u32(&pos,&b,buf));
               args.push_back(consume_pointer(&pos,&b,buf));
               //extra+=6;
            }

            printf("Prop type: %x %s\n", ptype, prop_types[ptype].c_str());
#if 1
            new SList(orel_pos,"property",&args);

            rel_pos+=0x14;
            printbytes(&buf[opos], esz+(pos-opos));
            continue;
#endif
        }else if(type==21){//range

            esz=0;
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_pointer(&pos,&b,buf,true));
            new SList(rel_pos,"range",&args);
        }else if(type==22){
            esz=0;
            args.push_back(consume_pointer(&pos,&b,buf));
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf));
            new SList(rel_pos,"group",&args);
        }else if(type==23){
            esz=0;
            args.push_back(consume_pointer(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf));
            new SList(rel_pos,"group_member",&args);
        }else if(type==32){
            esz=0;
            args.push_back(consume_pointer(&pos,&b,buf));
            new SList(rel_pos,"symbol",&args);
        }else if(type==33){
            esz=0;
            uint32_t orel_pos = rel_pos;
            args.push_back(consume_pointer(&pos,&b,buf,false,&rel_pos));
            args.push_back(consume_pointer(&pos,&b,buf,false,&rel_pos));
            new SList(orel_pos,"list",&args);

            printbytes(&buf[opos], esz+(pos-opos));
            continue;
        }else if(type==38){ //XXparentChild
            esz=0;
            args.push_back(consume_pointer(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf));
            new SList(rel_pos,"list",&args);
        }else if(type==52){ //zeLP
            esz=0;
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));

            new SList(rel_pos,"LP",&args);
            extra=0x10;
        }else if(type==65){ //zeLabel
            esz=0;
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));

            new SList(rel_pos,"label",&args);
        }else if(type==66){ //zeArc
            esz=0;
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_pointer(&pos,&b,buf,true));
        }else if(type==68){
            esz=0;
            uint32_t cnt = __bswap_32(*(uint32_t*)&buf[pos]);            
            pos+=4;
            b-=4;
            for(uint32_t j=0; j < cnt; j++){
               args.push_back(consume_u32(&pos,&b,buf));
               args.push_back(consume_u32(&pos,&b,buf));
            }
            new SList(rel_pos,"polygon",&args);
        }else if(type==71){ //zeLine
            esz=0;
            uint32_t pcnt = __bswap_32(*(uint32_t*)&buf[pos]);
            pos+=4;
            b-=4;
            for(uint32_t i=0; i < pcnt; i++){
               args.push_back(consume_pointer(&pos,&b,buf,true));
               args.push_back(consume_pointer(&pos,&b,buf,true));
            }
        }else if(type==74){ //zePath
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf,true));

            esz=0;
            uint32_t cnt = __bswap_16(*(uint16_t*)&buf[pos]);            
            pos+=2;
            b-=2;


            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_pointer(&pos,&b,buf,true));

            for(uint32_t j=0; j < cnt; j++){
               args.push_back(consume_pointer(&pos,&b,buf,true));
               args.push_back(consume_pointer(&pos,&b,buf,true));
            }
            new SList(rel_pos,"polygon",&args);
        }else if(type==80){ //zeNet
            esz=0;
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf,true));  
            extra+=0x14;
            new SList(rel_pos,"net",&args);

       }else if(type==81){ //zeSig
            esz=0;
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_u32(&pos,&b,buf));             
            extra += 8;
            new SList(rel_pos,"sig",&args);
        }else if(type==82){ //zeTerm
            esz=0;
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf));
            new SList(rel_pos,"term",&args);
            extra+=0x8;
        }else if(type==83){ //zePin
            esz=0;
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_pointer(&pos,&b,buf,true));
            extra+=4;
            new SList(rel_pos,"pin",&args);
        }else if(type==84){ //zeInstTerm
            esz=0;
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf,true));
        }else if(type==89){ //zeFig
            esz=0;
            uint8_t ftype = buf[pos];
            pos++;
            b--;
            args.push_back(consume_byte(&pos,&b,buf));
            uint8_t flen = buf[pos];
            pos++;
            b--;
            args.push_back(consume_byte(&pos,&b,buf));

            printf("FIG %x\n", ftype);

//0000: 59 0A FC E6 00 00 05 0A 59 00 01 00 2D 59 05 FC 09 00 00 00 1B **58 00 00 05 

            if(ftype==5 || ftype == 0x22 || ftype==0x1a || ftype==0xb || ftype==0x23){
               for(uint32_t j=0; j < 4; j++){
                  args.push_back(consume_u32(&pos,&b,buf));
               }
               args.push_back(consume_pointer(&pos,&b,buf,true));
            }else if(ftype==9 || ftype==0x21 || ftype==0xd || ftype==0x25){
               for(uint32_t j=0; j < 6; j++){
                  args.push_back(consume_pointer(&pos,&b,buf,true));
               }
            }else{
               args.push_back(consume_pointer(&pos,&b,buf,true));
               args.push_back(consume_pointer(&pos,&b,buf,true));
            }

            new SList(rel_pos,"fig",&args);

            rel_pos+=sizes32[type]+0x14;
            printbytes(&buf[opos], esz+(pos-opos));
            continue;
        }else if(type==91){ //zeTextDisplay
            esz=0;

            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_pointer(&pos,&b,buf,true));


            uint8_t flen = buf[pos];
            pos++;
            b--;
            for(uint32_t i=0; i < MAX(flen,0xF); i++)
               args.push_back(consume_byte(&pos,&b,buf));

        }else if(type == 92){ //zeInstHeader
            esz=0;
            args.push_back(consume_pointer(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf));
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf));


            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));

            extra=0x20;
            new SList(rel_pos,"inst_header",&args);
        }else if(type == 93){ //zeMosaic
            esz=0;
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_pointer(&pos,&b,buf,true));

            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_byte(&pos,&b,buf));

            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_pointer(&pos,&b,buf,true));

            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_pointer(&pos,&b,buf,true));

        }else if(type == 94){ //zeAnyInst
            esz=0;
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));

            args.push_back(consume_byte(&pos,&b,buf));
            uint8_t ftype = buf[pos];
            pos++;
            b--;
            if(ftype){
               args.push_back(consume_byte(&pos,&b,buf));
               args.push_back(consume_byte(&pos,&b,buf));
            }
            extra=0x8;
            new SList(rel_pos,"any_inst",&args);
        }else{
            printf("Unparsed type: 0x%x %d\n", type, type);
            printbytes(&buf[opos], esz+(pos-opos));
            //exit(0);
            assert(false);
        }

        if(frompos.find(rel_pos) == frompos.end()){
            new SList(rel_pos,string("unknown_") + types[stringidx[type]],&args);
        }


        printbytes(&buf[opos], esz+(pos-opos));
        uint32_t asz=esz+(pos-opos)+extra;
        if(asz%4)
          asz+=4-(asz%4);
         
        if(false){//type==20){//){//type==89){//Fig
           rel_pos += 0x54;
        }else{
           rel_pos += asz-4;
        }
        pos+=esz;
        b-=esz;
   }
}

int main(int argc, char** argv){
   //Load entire file into memory
   //FILE* f = fopen("LAYOUT.CDB","r");
   FILE* f = fopen(argv[1],"r");

   fseek(f,0,SEEK_END);
   size_t sz = ftell(f);
   fseek(f,0,SEEK_SET);
   uint8_t *buf = (uint8_t*)valloc(sz);
   fread(buf,sz,1,f);
   fclose(f);
   uint32_t srcid = *(uint32_t*)&buf[0x0];
   uint32_t maybe_len = *(uint32_t*)&buf[0x4];
   char* date = (char*)&buf[8];
   uint32_t nsegs = *(uint32_t*)&buf[0x20];
   uint32_t endian = *(uint32_t*)&buf[0x2C];
   char* text0 = (char*)&buf[0x30];


   endian = __bswap_32(endian);
   maybe_len = __bswap_32(maybe_len);
   nsegs = __bswap_32(nsegs);
 
   printf("SrcID: %X, Date: %s, Data Len: %d, Segments %X, Endian: %X, Txt: %s @%s\n", srcid, date, maybe_len, nsegs, endian, text0, argv[1]);

   uint64_t pos=0x80;
   for(uint32_t i=0; i < nsegs; i++){
       uint64_t seg_start=pos;
       //Seg is 0x40 bytes
       uint32_t e = __bswap_32(*(uint32_t*)&buf[pos+0x4]); //Checksum

       uint32_t a = __bswap_32(*(uint32_t*)&buf[pos+0xc]);
       uint32_t b = __bswap_32(*(uint32_t*)&buf[pos+0x10]);
       uint32_t c = __bswap_32(*(uint32_t*)&buf[pos+0x14]);
       uint32_t d = __bswap_32(*(uint32_t*)&buf[pos+0x18]);


       uint32_t compress = buf[pos+0x20];
       //if(0x20&1) compressed
       printf("Segment %x L:%x %x %x %lx %x %x, DCL: %x\n", a, b, c, d, pos, e, compress, d-0x18);

//       printbytes(&buf[pos], 0x50);

       printbytes(&buf[pos+0x0], 0x40);

       //Segment checksum
       uint32_t sum=0;
       for(uint32_t i=0; i < b; i++){
          sum = (((int8_t*)buf)[pos+i]) + ((int)sum)*3;
       }
       printf("Sum: %x\n", sum);

       pos+=0x40;
if(argc<3 || i==atoi(argv[2])){
       if((compress&1)==0){
          parseseg(buf,seg_start,pos,i, b);
       }else
          parsecseg(buf,seg_start,pos,i, b, argv[1]);
}
       pos+=b;
}
   //    assert((d-0x18) % esz == 0);
#endif

   printf("%x %x\n", pos, sz);
   
   uint32_t dangles=0;
   vector<SList*> allobjs;
   vector<uint32_t> tgts, refs;
   for(auto it=frompos.begin(); it!=frompos.end(); it++){
      //printf("%X\n", (*it).first);
      if((*it).first){
        allobjs.push_back((*it).second);
        tgts.push_back((*it).second->m_ofst);
      }
   }

   //exit(0);
   for(auto it=allobjs.begin(); it!=allobjs.end(); it++){
      if((*it)->m_tgt)
         continue;
      for(auto it2=(*it)->m_list.begin(); it2!=(*it)->m_list.end(); it2++){
         if(!(*it2)->m_tgt)
           continue;
         uint32_t tgt=(*it2)->m_tgt;
         refs.push_back(tgt);        
         SList* stgt = (*frompos.find(tgt)).second;
         if(!stgt){
           dangles++;
           continue;
         }
         *it2=stgt;
         consumed.insert(stgt->m_ofst);
      }
   }

#if 1
   sort(tgts.begin(), tgts.end());
   sort(refs.begin(), refs.end());
   printf("Tgts:\n");
   uint32_t last=0;
   uint32_t base=0x10000;
   uint32_t len=0x50000;
   for(auto it=tgts.begin(); it!=tgts.end(); it++)
      if(*it>=base && *it<base+len && *it != last){
         printf("%X %X\n", *it, *it - last);
         last=*it;
      }
   printf("Refs:\n");
   last=0;
   for(auto it=refs.begin(); it!=refs.end(); it++)
      if(*it>=base && *it<base + len && *it != last){
         printf("%X %X\n", *it, *it - last);
         last=*it;
      }
#endif

#if 1

   for(auto it=allobjs.begin(); it!=allobjs.end(); it++){
      //if(!(*it)->m_list.size())
      //   continue;
      if(consumed.find((*it)->m_ofst) != consumed.end())
         continue;
      print_reset(0);
      set<SList*> parents;
      (*it)->print(&parents);
      printf("\n");
   }
#endif

#if 0
   printf("%ld\n", sizeof(types)/sizeof(char*));

   for(int i=0; i < 97; i++){
      if(!stringidx[i])
         continue;
      printf("%16.16s\t%2d\t%3d\n", types[stringidx[i]],i,sizes32[i]);
   }
#endif
}
