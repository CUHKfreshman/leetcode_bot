import fs from 'fs/promises';
import path from 'path';
import { LeetCode, Problem } from 'leetcode-query';
// this is local interface for Problem in leetcode_data.json, not identical to the one in leetcode-query
interface ProblemLocal {
    stat: {
        question_id: number;
        question__article__live: string | null;
        question__article__slug: string | null;
        question__article__has_video_solution: boolean | null;
        question__title: string;
        question__title_slug: string;
        question__hide: boolean;
        total_acs: number;
        total_submitted: number;
        frontend_question_id: number;
        is_new_question: boolean;
    };
    status: string | null;
    difficulty: {
        level: number;
    };
    paid_only: boolean;
    is_favor: boolean;
    frequency: number;
    progress: number;
}
// this is the interface for the data in leetcode_data.json
interface LeetCodeData {
    user_name: string;
    num_solved: number;
    num_total: number;
    ac_easy: number;
    ac_medium: number;
    ac_hard: number;
    stat_status_pairs: ProblemLocal[];
    frequency_high: number;
    frequency_mid: number;
    category_slug: string;
}

class ProblemService {
  private static instance: ProblemService;
  private leetCodeData: LeetCodeData | null = null;
  private freeProblems: ProblemLocal[] = [];
  private leetcode: LeetCode | null = null;
  private constructor() {
      // Private constructor to prevent direct construction calls with the `new` operator.
  }

  public static async getInstance(): Promise<ProblemService> {
      if (!ProblemService.instance) {
          ProblemService.instance = new ProblemService();
          ProblemService.instance.leetcode = new LeetCode();
          await ProblemService.instance.loadData();
      }
      return ProblemService.instance;
  }

  private async loadData() {
      try {
          const data = await fs.readFile(path.join(__dirname, '../data/leetcode_data.json'), 'utf-8');
          this.leetCodeData = JSON.parse(data);
          if (!this.leetCodeData) {
              throw new Error('Failed to parse LeetCode data');
          }
          this.freeProblems = this.leetCodeData.stat_status_pairs.filter(problem => !problem.paid_only);
      } catch (error) {
          console.error('Error loading LeetCode data:', error);
      }
  }

  private async queryProblemDetails(slug: string): Promise<Problem | null> {
        if (!this.leetcode) {
            throw new Error('LeetCode API not loaded');
        }
        try {
            const problem = await this.leetcode.problem(slug);
            return problem;
        } catch (error) {
            console.error('Error fetching problem details:', error);
            return null;
        }
    }
  async getProblem(frontendQuestionId?: number): Promise<Problem | null> {
      if (!this.leetCodeData) {
          throw new Error('LeetCode data not loaded');
      }
      let randomProblem: ProblemLocal | null = null;
      if (frontendQuestionId) {
          randomProblem = this.leetCodeData.stat_status_pairs.find(problem => problem.stat.frontend_question_id === frontendQuestionId) || null;
      } else {
          randomProblem = this.freeProblems[Math.floor(Math.random() * this.freeProblems.length)] || null;
      }
      if( randomProblem === null) {
        throw new Error('Failed to fetch problem!');
    }
      // now query the problem details by slug
      return await this.queryProblemDetails(randomProblem.stat.question__title_slug);

  }
}

export default ProblemService;

// import { LeetCode, LeetCodeGraphQLQuery, LeetCodeGraphQLResponse } from 'leetcode-query';

// class problemService {
//   private leetcode: LeetCode;

//   constructor() {
//     this.leetcode = new LeetCode();
//   }

//   async getProblemService(questionId?: number): Promise<LeetCodeGraphQLResponse> {
//     try {
//       const query: LeetCodeGraphQLQuery = {
//         operationName: "randomQuestion",
//         variables: {
//           categorySlug: "",
//           filters: {}
//         },
//         // query is to get the problem by questionId
//         query: ` query randomQuestion($categorySlug: String, $filters: QuestionListFilterInput) 
//         {
//           randomQuestion(categorySlug: $categorySlug, filters: $filters) 
//           {
//             titleSlug
//           }
//         }
//         `
//       };
//       const titleSlug = await this.leetcode.graphql(query);
      
//       return problem;
//     } catch (error) {
//       console.error(`Error fetching problem(s):`, error);
//       throw new Error('Failed to fetch problem(s)!');
//     }
//   }
// }

// export default new problemService();