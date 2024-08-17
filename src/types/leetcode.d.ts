export namespace LeetCodeDataCollection {
    // this is local interface for Problem in leetcode_data.json, not identical to the one in leetcode-query
    export interface ProblemLocal {
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
    export interface LeetCodeMetaData {
        last_updated: string;
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
}
export type ProblemLocal = LeetCodeDataCollection.ProblemLocal;
export type LeetCodeMetaData = LeetCodeDataCollection.LeetCodeMetaData;