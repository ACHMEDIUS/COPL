# Behrad Kamalabadifarahani, s3323129 and Dylan Dingjan, s3693953
<h3>General information</h3>
<ul>
    <li>λ-calculus parser, interpreter and type checker</li>
    <li>Tested on python version 3.11 and Ubuntu 22.04 LTS</li>
    <li>For all assignments, the lambda character is represented by "λ". However both a backslash "\" and "λ".</li>
</ul>
<h3><strong>Assignment 1: λ-calculus standard format</strong></h3>
<p>The standard format used for the λ-calculus is the following:</p>
<p>Variables are represented by their names.</p>
<p>Lambda abstractions are represented by the keyword λ, followed by the variable name, followed by a dot, followed by the body of the abstraction.</p>
<p>Applications are represented by the function name followed by a space, followed by the argument.</p>
<p>For example, the expression (λx. x + 1) would be represented as λx.x+1 in the standard format.</p>
<p>To run the program, simply run:</p>

```bash
make run
```
<p>Alternativaly you could pre load an list of expressions as followed:</p>

```bash
make load_file FILE=<inputs>.zip
```
<h3><strong>Assignment 2: λ-calculus interpreter</strong></h3>
<p>The program reads zip files as an input. You could load a .zip file containing expressions and run the program as:</p> 

```bash
make load_file FILE=<inputs>.zip

```
<p>Alternativaly you could enter debug mode by just running the program as normal:</p>

```bash
make run
```
<h3><strong>Assignment 3: λ-calculus type checker</strong></h3>

### The tested inputs for each assignment can be viewed in "tested.txt"