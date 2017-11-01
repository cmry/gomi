# ec2latex
This python script is intended to convert an XML with conference submissions to a LaTeX book
of abstracts. Note that in it's current state at least some knowledge of LaTeX is required to
use it for your conference. -- [example](http://www.clips.uantwerpen.be/~ben/sites/default/files/book_of_abstracts_final.pdf)

## Files

Given that you have used a conference manager such as EasyChair, the submissions are usually
easily convertible to some XML format. This script will help you turn this into a compiled
LaTeX file with little effort. Currently, the version is very much in development and a lot
of manual labour is still needed. The important part of the file tree looks like this:

```
.
├── abstracts.xml
├── agenda.json
├── main.py
└── tex
    ├── adverts.tex
    ├── bos_i.tex
    ├── extraback.tex
    ├── preface.tex
    ├── sponsors
    │   ├── github.pdf
    │   └── github.svg
    ├── sponsors.tex
    ├── structure.tex
    ├── titleback.tex
    └── title.tex
```

#### abstracts.xml

This file gives one example of a submission and how it should look in XML.

#### agenda.json

This gives an example of the agenda structure that can be used to generate
a programme in the LaTeX file. Please note that currently they need to be
set by hand: you can add, remove or change the names, times and sessions
and provide a list of id's from `abstracts.xml` for each block where they 
should be in.

#### main.py

This is the master python file; this needs to be pretty much left alone but
one can add for example some custom string replacements in the `sanitize.cust`
dictionary.

#### tex - adverts.tex

These are adverts of gold and silver sponsors, they can be tweaked to fit
the page formats and some text can be manually provided. Comment out 
`\input{sponsors}` in `bos_o.tex` if you do no want this.

#### tex - bos_i.tex

This is the master .tex file; please make changes to the `custom vars` section
before running `main.py`: the script will fill out specific comment blocks with 
tex code.

#### tex - extraback.tex

Lists people who have worked on the conference and the previous versions of it.
Currently these need to be manually added. Comment out `\input{extraback}` in 
`bos_o.tex` if you do no want this.

#### tex - preface.tex

Replace the written text with your own to form a preface. Comment out `\input{preface}` 
in `bos_o.tex` if you do no want this.

#### sponsors

Can be used to dump images for the sponsor pages; currently the github svg is in
there as placeholder material.

#### tex - sponsors.tex

This lists all the sponsors for the conference, some examples are given on how
to resize images and such. Need to be manually changed. Comment out `\input{sponsors}` 
in `bos_o.tex` if you do no want this.

#### tex - titleback.tex

Accredits people who have worked on the conference (and this package by default).
Currently some names need to be set by hand. Comment out `\input{titleback}` in `bos_o.tex` 
if you do no want this; referring to this package would be great though :)

#### tex - title.tex

Title page. comment out `\input{title}` in `bos_o.tex` to not even have a title.

## Usage

Follow these steps for compiling a first test version:

``` shell
$ git clone https://github.com/fazzeh/ec2latex
$ cd ec2latex
$ python main.py
$ cd tex
$ pdflatex bos_o.tex
```

Now you can open `bos_o.pdf` from the `tex` folder with your pdf viewer of choice.

## What now?

Fill `abstracts.xml` with submissions, and fill out `agenda.json` by hand so that
submissions are assigned to certain sessions. In the end, [this](http://www.clips.uantwerpen.be/~ben/sites/default/files/book_of_abstracts_final.pdf)
is what it could look like.

## Closer look at agenda.json

Editing `agenda.json` should be straightforward. `"agenda"`, as well
as the ID numbers for each block (`01` and `02` here) remain unchanged.
Blocks are applied horizontally, and make one row in your programme
table. They are given a name and a time. If you provide `"sessions"`,
these need to be ID'ed as well (`"s01"` - `"s05"` here). These will be
applied vertically and will make up the columns in your programme. Give
them a name and a location, and then manually fill out the `"blocks"`
list with IDs from the `abstracts.xml` in accordance to which session
they belong. If there are any indexing errors with less entries, please
file an issue on github.

``` json
{ 
	"agenda": {
		"01": {
		    "name": "Registration + coffee",
			"time": "9:00 - 9:30"
		}, 
		"02": {
	        "name": "Session 1",
			"time": "9:30 - 10:50",
			"sessions": {
				"s01": {
					"name": "Spelling \\& Normalization",
					"room": "R.212",
					"blocks": [11, 63, 81, 32]
				}, 
				"s02": {
					"name": "Computational Psycholinguistics",
					"room": "R.124",
					"blocks": [35, 42, 85, 21]
				}, 
				"s03": {
					"name": "Syntax",
					"room": "R.125",
					"blocks": [17, 56, 55, 83]
				}, 
				"s04": {
					"name": "Opinion",
					"room": "R.213",
					"blocks": [64, 77, 89, 40]
				}, 
				"s05": {
					"name": "Speech \\& Discourse",
					"room": "R.224",
					"blocks": [7, 12, 51, 68]
				}
			}
		},
```