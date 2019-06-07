/***********************************************************************************[Minumerate.cc]
Copyright (c) 2011, Niklas Sorensson

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT
OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
**************************************************************************************************/

#include <stdio.h>
#include "Minumerate.h"

using namespace Minisat;


static void initUpperBound  (const Solver& s, vec<bool>& ub, vec<Lit>& ub_false)
{
    ub.clear(); ub.growTo(s.nVars(), true);
    ub_false.clear();
}


static void updateUpperBound(Solver& s, vec<bool>& ub, vec<Lit>& ub_false)
{
    ub.clear();
    for (int i = 0; i < s.nVars(); i++)
        if (s.modelValue(i) == l_False && ub[i]){
            ub[i] = false;
            ub_false.push(~mkLit(i));
        }

    vec<Lit> blocking_clause;
    for (int i = 0; i < s.nVars(); i++)
        if (ub[i])
            blocking_clause.push(~mkLit(i));
    s.addClause(blocking_clause);
}


// Enumerate and count all minimal models:
uint64_t minimalModelCount(Solver& s, bool use_preferred_polarity, FILE *f)
{
    vec<bool> upperbound_model;
    vec<Lit>  ub_false;
    uint64_t  num_models = 0;

    if (use_preferred_polarity)
        // Adjust preferred polarity:
        for (int i = 0; i < s.nVars(); i++)
            s.setPolarity(i, l_True);

    if (s.solve()) {
        // There is some minimal model left, reduce the current model:
        initUpperBound  (s, upperbound_model, ub_false);
        updateUpperBound(s, upperbound_model, ub_false);

        while (s.solve(ub_false))
            updateUpperBound(s, upperbound_model, ub_false);

        // NOTE: the minimal model can be read from 'upperbound_model' at this point.
        if (f != NULL) {
            for (int i = 0; i < s.nVars(); i++)
                if (s.model[i] != l_Undef)
                    fprintf(f, "%s%s%d", (i==0)?"":" ", (s.model[i]==l_True)?"":"-", i+1);
            fprintf(f, " 0\n");
        }

        num_models++;
    }
    return num_models;
}


// Enumerate and count all minimal models:
uint64_t allModelCount(Solver& s, FILE *f)
{
    vec<Lit>  blocking_clause;
    uint64_t  num_models = 0;

    while (s.solve()){
        // Create blocking clause from the current model to rule that out in the future:
        blocking_clause.clear();
        for (int i = 0; i < s.nVars(); i++)
            blocking_clause.push(mkLit(i, s.modelValue(i) == l_True));
        s.addClause(blocking_clause);

        // NOTE: the minimal model can be read from 'upperbound_model' at this point.
        if (f != NULL) {
            for (int i = 0; i < s.nVars(); i++)
                if (s.model[i] != l_Undef)
                    fprintf(f, "%s%s%d", (i==0)?"":" ", (s.model[i]==l_True)?"":"-", i+1);
            fprintf(f, " 0\n");
        }
        // if (f != NULL) {
        //     TrailIterator iter = s.trailBegin();
        //     for (int i = 0; i < s.nAssigns(); ++i, ++iter) {
        //         Lit l = *iter;
        //         fprintf(f, "%s%s%d", (i==0)?"":" ", sign(l)?"":"-", var(l) + 1);
        //     }
        //     fprintf(f, " 0\n");
        // }

        num_models++;
    }
    return num_models;
}
