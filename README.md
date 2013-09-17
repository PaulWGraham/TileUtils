# TileUtils #
by Paul Graham 
graham.paul+github@gmail.com

## What Is It? ##

TileUtils is an experimental proof of concept that explores the idea of translating individual tiles in a tilemap created with Tiled (http://www.mapeditor.org) into abstract data using a translation table.

## How it works ##

The TileUtils proof of concept works by translating .tmx tilemaps into arbitrary data using a .ttt translation table. 

## The .ttt File Format ##
An example of a .ttt file:
    <?xml version="1.0" encoding="UTF-8"?>
    <tiletranslationtable name="test" version="0.1">
        <defaulttranslations />
        <tilesettranslations>
            <tilesettranslation tilesetname="test">
                <tiletranslation tilename="one">
                    <values>
                        <blenderObjectFromScene>../Objects/standard/blender/rampOneOne/pixen/rampOneOneU.blend/Object/rampOneOneU</blenderObjectFromScene>
                    </values>
                </tiletranslation>
                <tiletranslation tilename="two">
                    <values>
                        <blenderObjectFromScene>../Objects/standard/blender/rampOneOne/pixen/rampOneOneR.blend/Object/rampOneOneR</blenderObjectFromScene>
                    </values>
                </tiletranslation>
                <tiletranslation tilename="three">
                    <values>
                        <blenderObjectFromScene>../Objects/standard/blender/rampOneOne/pixen/rampOneOneD.blend/Object/rampOneOneD</blenderObjectFromScene>
                    </values>
                </tiletranslation>
                <tiletranslation tilename="four">
                    <values>
                        <blenderObjectFromScene>../Objects/standard/blender/rampOneOne/pixen/rampOneOneL.blend/Object/rampOneOneL</blenderObjectFromScene>
                    </values>
                </tiletranslation>
            </tilesettranslation>
        </tilesettranslations>
    </tiletranslationtable>


## Installation ##

This section is meant to document the installation procedure I used for this experiment. Being an experimental installation there was no known best way to install it when I developed it. TileUtils was developed on Mac OS 10.8.4.

The installation procedure I used can be broken down into the following general steps:

1.  Install Python 3
2.  Install pip-3.3
3.  Configure pip-3.3
4.  Install TileUtils
5.  Configure TileUtils
6.  Install Blender
7.  Configure Blender
8.  Install Tiled
9.  Configure Tiled

The above steps in more detail:

1.  Install Python
I actually did this a long time ago. I simply downloaded the installer from the python website (http://www.python.org/download/) and ran it. This step is included for the sake of completeness.

2.  Install pip-3.3
I installed pip-3.3 by following the instructions on the pip website (http://www.pip-installer.org/en/latest/installing.html). The only subtly being that whenever the instructions called for the python interpreter to be used I substituted python3.

3.  Configure pip-3.3
After installing pip-3.3 I tried running it by typing pip-3.3 into the command line but it didn't work. After some research I discovered that pip-3.3 had successfully installed but wasn’t on the path. I fixed this by creating ~/.bash_profile and adding:

    export PATH=$PATH:/Library/Frameworks/Python.framework/Versions/3.3/bin/

to it.

4.  Install TileUtils
Once pip-3.3 was installed I used it to install the TileUtils package. I did this with the following command:

pip-3.3 install TileUtils-0.0.1.tar.gz 

5.  Configure TileUtils
The executable scripts in TileUtils were not by default installed in a location that was on the path. Like pip-3.3, the TileUtils scripts were installed to  /Library/Frameworks/Python.framework/Versions/3.3/bin/ which fortunately was added to the path in step 3.

6.  Install Blender
I downloaded and installed Blender 2.68a for Mac OS X Intel 64 bit from the Blender website (http://www.blender.org/download/get-blender/) and installed it according to the instructions on the site.

7.  Configure Blender
Blender came with its own version of python. By default the version of python included with Blender did not access the same build environment as the version of python installed on my Mac. This meant that when an executable script from TileUtils was run in Blender it (the script) could not access the necessary library modules in the TileUtils package. I added access to the entire TileUtils package to the Blender Python environment by creating a symbolic link to the TileUtils directory (located in the system site-packages directory) in the scripts/addons/modules directory in the blender app bundle by using the following commands:

    cd /Applications/blender.app/Contents/MacOS/2.68/scripts/addons/modules/

    ln -s /Library/Frameworks/Python.framework/Versions/3.3/lib/python3.3/site-packages/TileUtils

8.  Install Tiled
I installed Tiled 0.9.1 by dragging the Tiled executable onto the Applications folder shortcut in the DMG I had downloaded from the Tiled website (http://www.mapeditor.org/download.html).

9.  Configure Tiled
There were a few things I did to configure Tiled. The first was to create a new tilemap and select “XML” as the layer format  (it’s the format that TileUtils understands). Luckily, Tiled saves this selection and uses it as the default option for any new tilemaps. 
    I then created some custom commands (https://github.com/bjorn/tiled/wiki/Using-Commands). The first custom command I created was one to run tileplacer.py using Blender to translate the current map. Normally, the process of running tileplacer.py using Blender from the command line (see: tileplacer.py) would look something like the following:

export TILEPLACER_ARGS="'/Users/paul/Documents/Programming/Level Editor/Tiles And Objects/structured/Examples/all.tmx' '/Users/paul/Documents/Programming/Level Editor/Tiles And Objects/structured/Translations/standard.ttt'  blenderObjectFromScene --env blender --steps 1 1 2"

    '/Applications/blender.app/Contents/MacOS/blender' -P '/Library/Frameworks/Python.framework/Versions/3.3/bin/tileplacer.py'

unset TILEPLACER_ARGS

Unfortunately, this process wouldn’t work as a Tiled custom command. This is why I created the ertileplacer.py script (see: ertileplacer.py). ertileplacer.py is a wrapper that allows for the tileplacer.py to be run in the mode described above but without the need for multiple command lines and without the need to set an environment variable in the Terminal.
    With ertileplacer.py I was able to create the custom command line to translate the current map by running tileplacer.py through Blender. The custom command line looked like this:

    /Library/Frameworks/Python.framework/Versions/3.3/bin/ertileplacer.py "/Applications/blender.app/Contents/MacOS/blender -P /Library/Frameworks/Python.framework/Versions/3.3/bin/tileplacer.py" %mapfile "/Users/paul/Documents/Programming/Level Editor/Tiles And Objects/structured/Translations/standard.ttt" blenderObjectFromScene --env blender --steps 1 1 2

When I set the command above as the first enabled custom command it became the default command that was run when I clicked the custom command button or pressed F5.

## Utilities ##

### dirttt.py ###

    dirttt.py   [-h] [--csv] [--env {default,blender}] [--errors]
                [--nodefaults] [--save SAVE] DIR

A utility used to generate a translation table from the contents of a directory tree. The name of the directory DIR is used as the name of the translation table. The names of the directories contained directly in DIR are used as the names of the tilesets with the exception of the directory named DEFAULTS which, if present in DIR is used to generate the defaulttranslations section of the translation table. The names of the directories directly in the tileset directories are used as the translation types present in that particular tileset. The translation type directories are then recursively searched and any non-directory files found are (possibly) used to generate tile translation values. The names of the files found are used to generate the names of the tiles and the content of the files is used to create the translation values.

If --save is used the data generated for the translation values is created relative to the directory that file SAVE is in. This is differs from the default behavior of creating the generated data relative to DIR.

dirttt.py can be extended to support new environments and/or translation types by subclassing TileTranslationCreator and registering an instance of the new class with the directoryConverter object.


### csvttt.py ###
    csvttt.py [-h] [--save SAVE] CSV

 A utility that converts a translation table in csv format to ttt format.

### ertileplacer.py ###
    ertileplacer.py     [-h] [--env ENV] [--link] [--nodefaults]
                        [--remap REMAP REMAP] [--save SAVE]
                        [--steps STEPS STEPS STEPS]
                        commandwithargs tilemap translationtable
                        translationtype

A wrapper used to run tileplacer.py (see: tileplacer.py) using a custom command in Tiled. 


### tileplacer.py ###
    tileplacer.py   [-h] [--env {blender,maya,terminal}] [--link]
                    [--nodefaults] [--remap REMAP REMAP] [--save SAVE]
                    [--steps STEPS STEPS STEPS]
                    tilemap translationtable translationtype

The main script of the TileUtils package. tilepplacer.py translates a map and uses the translated data to produce output. What ouput is produced depends on the environment type and type of translation.

tileplacer.py is a versatile script and depending on the environment type may be run from the command line or by an embedded python interpreter (e.g. Blender).

If the environment variable TILEPLACER_ARGS is set tileplacer.py will look there for its arguments rather than the command line.

tileplacer.py can be extended to support new environments and/or translation types by subclassing EnvironmentSetter and/or StandardPlacer and registering instances of the new classes with the tilePlacer object.


### tttcsv.py ###
    tttcsv.py [-h] [--save SAVE] TRANSLATIONTABLE

A utility that converts a translation table in ttt format to csv format.

## Copyright ##
Copyright (c) 2013 Paul Graham 

All material in this git repository is subject to a version of the MIT License.

See LICENSE for details.