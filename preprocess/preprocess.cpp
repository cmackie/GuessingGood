#include <cmath>
#include <climits>
#include <iostream>
#include <iomanip>
#include <fstream>
#include <vector>

using namespace std;

#include "cnf_io.hpp"

class sat {
private:
    int l_num;
    int* l_c_num;
    int* l_c_sum;
    int* l_val;

    int get_clause(int i_clause, int** clause) {
      *clause = l_val + l_c_sum[i_clause];
      return l_c_num[i_clause];
    }
public:
    int v_num;
    int c_num;

    sat(const string& cnf_path) : l_num(0), v_num(0), c_num(0) {
      bool error = cnf_header_read(cnf_path, &v_num, &c_num, &l_num);

      if (error)
        throw "Parse error";

      l_c_num = new int[c_num];
      l_val = new int[l_num];
      cnf_data_read(cnf_path, v_num, c_num, l_num, l_c_num, l_val);

      l_c_sum = new int[c_num];
      l_c_sum[0] = 0;
      for (int i = 1; i < c_num; i++)
        l_c_sum[i] = l_c_sum[i - 1] + l_c_num[i - 1];
    }

    vector<int> filter_clauses(const vector<int>& in, bool (*predicate)(const int l_clause, const int* clause)) {
      int l_clause;
      int* clause;
      vector<int> out;
      out.reserve(((unsigned int)c_num));
      for (int i : in) {
        l_clause = get_clause(i, &clause);
        if (predicate(l_clause, clause))
          out.push_back(i);
      }

      return out;
    }

    vector<int> contains_clauses(const vector<int>& in, int lit) {
      int l_clause;
      int* clause;
      vector<int> out;
      out.reserve(((unsigned int)c_num));
      for (int i : in) {
        l_clause = get_clause(i, &clause);
        for (int j = 0; j < l_clause; j++) {
          if (clause[j] == lit) {
            out.push_back(i);
            continue;
          }
        }
      }

      return out;
    }

    double sum_map(const vector<int>& in, double (*map)(const int l_clause, const int* clause)) {
      int l_clause;
      int* clause;
      double sum = 0;
      for (int i : in) {
        l_clause = get_clause(i, &clause);
        sum += map(l_clause, clause);
      }

      return sum;
    }

    int max_map(const vector<int>& in, int (*map)(const int l_clause, const int* clause)) {
      int l_clause;
      int* clause;
      int max = INT_MIN;
      for (int i : in) {
        l_clause = get_clause(i, &clause);
        int m = map(l_clause, clause);
        if (m > max)
          max = m;
      }

      return max;
    }

    int min_map(const vector<int>& in, int (*map)(const int l_clause, const int* clause)) {
      int l_clause;
      int* clause;
      int min = INT_MAX;
      for (int i : in) {
        l_clause = get_clause(i, &clause);
        int m = map(l_clause, clause);
        if (m < min)
          min = m;
      }

      return min;
    }
};

void analyze(const string& prob_path) {
  ofstream feat_file (prob_path + ".feat");
  sat* prob;
  try {
    prob = new sat(prob_path + ".cnf");
  } catch (const char* msg) {
    cerr << msg << endl;
    return;
  }

  // Create filtered clause lists
  vector<int> all;
  all.reserve((unsigned int)prob->c_num);
  for (int i = 0; i < prob->c_num; i++)
    all.push_back(i);

  vector<int> c1 = prob->filter_clauses(all, [](const int l_clause, const int* clause) {
      return l_clause == 1;
  });

  vector<int> c2 = prob->filter_clauses(all, [](const int l_clause, const int* clause) {
      return l_clause == 2;
  });

  vector<int> c3 = prob->filter_clauses(all, [](const int l_clause, const int* clause) {
      return l_clause == 3;
  });

  vector<int> c4 = prob->filter_clauses(all, [](const int l_clause, const int* clause) {
      return l_clause == 4;
  });

  vector<int> horn = prob->filter_clauses(all, [](const int l_clause, const int* clause) {
      int num_pos = 0;
      for (int i = 0; i < l_clause; i++) {
        if (clause[i] > 0)
          num_pos++;
        if (num_pos > 1)
          return false;
      }

      return true;
  });

  vector<int> antihorn = prob->filter_clauses(all, [](const int l_clause, const int* clause) {
      int num_neg = 0;
      for (int i = 0; i < l_clause; i++) {
        if (clause[i] < 0)
          num_neg++;
        if (num_neg > 1)
          return false;
      }

      return true;
  });

  vector<int> phis[] = {c1, c2, c3, c4, horn, antihorn, all};

  // Write formula level features
  feat_file << "FORMULA" << endl;
  for (const vector<int>& phi : phis)
    feat_file << phi.size() << " ";
  feat_file << endl;

  // Write variable level features
  for (int v = 1; v <= prob->v_num; v++) {
    feat_file << "VARIABLE " << v << endl;
    vector<int> lits = {v, -v};
    for (int lit : lits) {
      for (const vector<int>& phi : phis) {
        vector<int> cs = prob->contains_clauses(phi, lit);

        if (cs.empty()) {
          feat_file << "0 0 0 0 0 0 0 0 ";
        } else {
          feat_file << cs.size() << " ";
          feat_file << prob->sum_map(cs, [](const int l_clause, const int* clause) {
              return 1 / (double)l_clause;
          }) << " ";
          feat_file << prob->max_map(cs, [](const int l_clause, const int* clause) {
              return l_clause;
          }) << " ";
          feat_file << prob->min_map(cs, [](const int l_clause, const int* clause) {
              return l_clause;
          }) << " ";
          feat_file << prob->sum_map(cs, [](const int l_clause, const int* clause) {
              return pow(2, -l_clause);
          }) << " ";

          vector<int> pos = prob->filter_clauses(cs, [](const int l_clause, const int* clause) {
              int num_pos = 0;
              int num_neg = 0;
              for (int i = 0; i < l_clause; i++) {
                if (clause[i] > 0)
                  num_pos++;
                else if (clause[i] < 0)
                  num_neg++;
              }

              return num_pos > num_neg;
          });

          vector<int> neg = prob->filter_clauses(cs, [](const int l_clause, const int* clause) {
              int num_pos = 0;
              int num_neg = 0;
              for (int i = 0; i < l_clause; i++) {
                if (clause[i] > 0)
                  num_pos++;
                else if (clause[i] < 0)
                  num_neg++;
              }

              return num_pos < num_neg;
          });

          vector<int> zero = prob->filter_clauses(cs, [](const int l_clause, const int* clause) {
              int num_pos = 0;
              int num_neg = 0;
              for (int i = 0; i < l_clause; i++) {
                if (clause[i] > 0)
                  num_pos++;
                else if (clause[i] < 0)
                  num_neg++;
              }

              return num_pos == num_neg;
          });

          feat_file << pos.size() << " ";
          feat_file << neg.size() << " ";
          feat_file << zero.size() << " ";
        }
      }
    }
    feat_file << endl;
  }
}

int main(int argc, char* argv[]) {
  if (argc != 2)
    return EXIT_FAILURE;
  else {
    analyze(argv[1]);
    return EXIT_SUCCESS;
  }
}
