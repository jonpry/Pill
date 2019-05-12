## Intro

   Pill is an opensource interpreter for the Cadence Skill language. Particular targeting being able to run PCell generator codes used in VLSI. Pill is written in Python and compiles the source into Python bytecode where it is then executed alongside of regular python functions at similar speed to "native" python codes". Geometry functions are called throught the klayout API to yield usable gds. 
  
  The process of importing PDK codes and then validating the results is tedious. At this time, Pill is more of a tool to help you create a working klayout based PDK than an out of the box solution to import. 
  
  ## Requirements
  Python 2.7
  Klayout built with Python 2.7 
  Parsimonious
   
   ## Getting started
   First you must extract a bunch of data from PDK and make appropriate edits to entry.py. Which is a template file for cell generation. 
   1.  Find your layermap file. Pill knows how to read files with '#' comments and 4 element tuples describing each layer. Such as:
```
 ref		drawing		0	0`
```
   Copy this file into the pill directory
   In entry.py, change `layermap_file` to the filename
   2.  In virtuoso, run:

```
    dbOpenBag(ddGetObj("@lib","@cell"))~>prop~>??
```

Copy and paste the output into yourcell_props.il then edit `props_file` in entry.py to this file name

   3. In virtuoso, run: 
   ```
dbDumpPcDefinePcell(dbOpenCellViewByType("@lib" "pch" "layout" "maskLayout") "/tmp/pch.il")
```
4. Open the resulting file. There should be 3 primary sections, the first being a description of the cell. The second is a list of triplet parameters, and the third is code. The triplets needs to be cut and pasted into the `defaults =` section of the entry.py. Typically the code section just wraps a single function call. In which case we will make the target of that call our `func=`. 
5. Extract code. Using the pp(functionName) to pretty print the skill of interest. Create a .il file with the function. In practice this function will call many other PDK functions that must also be exported. It is best to not have functions that self reference in the same file, so you will end up with several files that must be loaded in a specific order. These will be listed in the `codes=[]`
6. Execute entry.py and hopefully the pcell will be generated
7. In your props.il there will be at least one function near the text "callback", this function should also be exported to allow the default parameters to be modified. 

##Notes

The compiler is fairly slow, so the compiled bytecode objects are cached, the next run will thus be faster. If you need to force a recompile, only needed if codegen changes, not if runtime functions are merealy modified, then bump the iversion. Modified skill files are automatically recompiled. 

The Skill language is difficult to parse, and the meaning of statements changes drastically if an identifier turns out to be a function or not. In many cases a parse error will be caused by the fact that things not declared as functions are assumed to be variables. In the region of the parsing error is a good place for something not defined, Which may either be another PDK function you need to export, or a missing runtime function. 

Sometimes functions needs to be defined, but don't need to exist.  for example these "xxxx_customer_Callback" kind of things. To overcome these issues, before calling cload() interp.skill.procedures['xxxx_customer_Callback'] = None

##Python interop
Skill calls python code through the interp.skill.procedures dictionary, which is largely populated in runtime.py. Type are largely native or can be coorced into native types and very little needs to be done in order to marshal things in/out of the python world. In some rare cases a piece of code will call ~> on something that is actually a list, in which case returned lists should be instances of tools.SkillDeref instead. 
