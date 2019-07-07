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

const char *types[] = { "0", "char", "short", "int", 
                        "long", "float", "double", "pointer",
                        "byte", "car", "cdr", "LPType", 
                        "MX", "MXR90", "MY", "MYR90", 
                        
                        "PCB", "XXString", "XXfreeObject", "XXfreeObject2", 
                        "XXgroup", "XXgroupMember", "XXilList", "XXilSymbol", 
                        "XXparentChild", "XXpropVal", "XXpropery", "XXrange", 
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
                     0, 0, 0x34, 0x44, 0x1c, 0, 0, 0,
                     0, 0, 0, 0, 0x20, 0x1c, 0x30, 2,
                     2, 0x14, 0x28, 0x10, 0xc, 0x10, 0, 0xc,
                     0, 0, 0x18, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0x20, 0x10, 0x14, 0x14,
                     0x14, 0xc, 8, 0x14, 0x30, 0x20, 0x1c, 0x2c,
                     0x44, 0x30, 0x20, 8};

uint32_t stringidx[] = {1, 1, 2, 2, 3, 3, 4, 4, 
                        5, 5, 6, 6, 7, 7, 8, 8,
                        0x1c, 0, 0x13, 0x12, 0x1a, 0x1b, 0x14, 0x15,
                        0, 0, 0, 0, 0, 0, 0, 0,
                        0x17, 0x16, 0x4B, 0x4B, 0x4A, 0x4A, 0x18, 0,
                        0x11, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0x13b, 0x150, 0x145, 0, 0, 0,
                        0, 0, 0, 0, 0x14f, 0x13f, 0x137, 0x14c,
                        0x14c, 0x146, 0x13a, 0x13c, 0x15a, 0x154, 0, 0x147, 
                        0, 0, 0x155, 0, 0, 0, 0, 0,
                        0x14d, 0x15b, 0x15c, 0x157, 0x144, 0x143, 0x152, 0x156, 
                        0x151, 0x13d, 0x153, 0x15d, 0x140, 0x14b, 0x138, 0x149,
                        0x148, 0, 0, 0}; 

void printbytes(uint8_t *buf, uint32_t len){
   for(uint32_t i=0; i < len; i+=16){
      printf("%4.4X: ", i);
      for(uint32_t j=0; j < 16; j++){
         printf("%2.2X ", buf[i+j]);
      }
      printf("\n");
   }
}

int main(){
   //Load entire file into memory
   FILE* f = fopen("PROP.XX","r");
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
 
   printf("SrcID: %X, Date: %s, Data Len: %d, Segments %X, Endian: %X, Txt: %s\n", srcid, date, maybe_len, nsegs, endian, text0);

   uint64_t pos=0x80;
   for(uint32_t i=0; i < nsegs; i++){
       //Seg is 0x40 bytes
       uint32_t e = __bswap_32(*(uint32_t*)&buf[pos+0x4]); //Checksum

       uint32_t a = __bswap_32(*(uint32_t*)&buf[pos+0xc]);
       uint32_t b = __bswap_32(*(uint32_t*)&buf[pos+0x10]);
       uint32_t c = __bswap_32(*(uint32_t*)&buf[pos+0x14]);
       uint32_t d = __bswap_32(*(uint32_t*)&buf[pos+0x18]);


       uint32_t compress = buf[pos+0x20];
       //if(0x20&1) compressed
       printf("Segment %x %x %x %x %lx %x %x, DCL: %x\n", a, b, c, d, pos, e, compress, d-0x18);

       printbytes(&buf[pos+0x0], 0x40);

       pos+=0x40;
       printbytes(&buf[pos], 0x40);

       //Segment checksum
       uint32_t sum=0;
       for(uint32_t i=0; i < b; i++){
          sum = (((int8_t*)buf)[pos+i]) + ((int)sum)*3;
       }
       printf("Sum: %x\n", sum);

       //Some kind of element header
       uint32_t type = __bswap_16(*(uint16_t*)&buf[pos+0x2]);
       uint32_t esz = sizes32[type];
       uint32_t ea = __bswap_32(*(uint32_t*)&buf[pos + 0x14]);

       
for(int j=0x18; j < 0x19; j++){
       uint32_t eb = __bswap_16(*(uint16_t*)&buf[pos+0xe +j]);
       uint32_t ec = __bswap_16(*(uint16_t*)&buf[pos+0x18+j]);
       uint32_t ed = __bswap_16(*(uint16_t*)&buf[pos+0x28+j]);
       uint32_t ee = __bswap_16(*(uint16_t*)&buf[pos+0x12+j]);

       printf("El Type: %x,%s, TS: %d, %x %x %x %x 12:%x\n", type, types[stringidx[type]], esz, ea, eb, ec, ed,ee);
}
   //    assert((d-0x18) % esz == 0);

       pos+=b;
   }
#if 0

   printf("%ld\n", sizeof(types)/sizeof(char*));

   for(int i=0; i < 97; i++){
      if(!stringidx[i])
         continue;
      printf("%16.16s\t%2d\t%3d\n", types[stringidx[i]],i,sizes32[i]);
   }
#endif
}
