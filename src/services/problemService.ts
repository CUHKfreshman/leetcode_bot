import fs from "fs/promises";
import path from "path";
import { LeetCode, Problem, DailyChallenge } from "leetcode-query";
import TranslationCNService from "./translationCNService";
import { ProblemLocal, LeetCodeMetaData } from "../types";
class ProblemService {
    // This is a singleton class
    private static instance: ProblemService;
    private leetCodeMetaData: LeetCodeMetaData | null = null;
    private freeProblems: ProblemLocal[] = [];
    private leetcode: LeetCode | null = null;
    private translatorCN: TranslationCNService | null = null;
    private constructor() {
        // Private constructor to prevent direct construction calls with the `new` operator.
    }

    public static async getInstance(): Promise<ProblemService> {
        if (!ProblemService.instance) {
            ProblemService.instance = new ProblemService();
            ProblemService.instance.translatorCN = new TranslationCNService();
            ProblemService.instance.leetcode = new LeetCode();
            await ProblemService.instance.loadData();
        }
        return ProblemService.instance;
    }

    private async loadData() {
        try {
            this.leetCodeMetaData = await this.fetchProblemListMetaData();
            if (!this.leetCodeMetaData) {
                console.log("Failed to fetch LeetCode data, trying local data...");
                const localData = await fs.readFile(
                    path.join(__dirname, "../data/leetcode_data.json"),
                    "utf-8"
                );
                this.leetCodeMetaData = JSON.parse(localData);
                if(!this.leetCodeMetaData) {
                    throw new Error("Failed to load local data & fetch LeetCode data");
                }
            }

            this.freeProblems = this.leetCodeMetaData.stat_status_pairs.filter(
                (problem) => !problem.paid_only
            );
        } catch (error) {
            console.error("Error loading LeetCode data:", error);
        }
    }
    private async queryProblemDetails(slug: string): Promise<Problem | null> {
        if (!this.leetcode || !this.translatorCN) {
            throw new Error("LeetCode API or translator not loaded");
        }
        try {
            const problem = await this.leetcode.problem(slug);

            const translationCN =
                await this.translatorCN.queryProblemTranslationCN(slug);
            if (!translationCN) {
                throw new Error("Failed to fetch Chinese translation");
            }
            problem.translatedTitle =
                translationCN?.data?.question?.translatedTitle || null;
            problem.translatedContent =
                translationCN?.data?.question?.translatedContent || null;
            return problem;
        } catch (error) {
            console.error("Error fetching problem details:", error);
            return null;
        }
    }
    async getPaidOnlyProblemsNumberList(): Promise<number[]> {
        if (!this.leetCodeMetaData) {
            throw new Error("LeetCode data not loaded");
        }
        return this.leetCodeMetaData.stat_status_pairs
            .filter((problem) => problem.paid_only)
            .map((problem) => problem.stat.frontend_question_id);
    }
    async getProblem(frontendQuestionId?: number): Promise<Problem | null> {
        if (!this.leetCodeMetaData) {
            throw new Error("LeetCode data not loaded");
        }
        let randomProblem: ProblemLocal | null = null;
        if (frontendQuestionId) {
            randomProblem =
                this.leetCodeMetaData.stat_status_pairs.find(
                    (problem) =>
                        problem.stat.frontend_question_id === frontendQuestionId
                ) || null;
        } else {
            randomProblem =
                this.freeProblems[
                    Math.floor(Math.random() * this.freeProblems.length)
                ] || null;
        }
        if (randomProblem === null) {
            throw new Error("Failed to fetch problem!");
        }
        // now query the problem details by slug
        return await this.queryProblemDetails(
            randomProblem.stat.question__title_slug
        );
    }

    async getDailyChallenge(): Promise<DailyChallenge> {
        if (!this.leetcode || !this.translatorCN) {
            throw new Error("LeetCode API or translator not loaded");
        }
        try {
            const dailyChallenge = await this.leetcode.daily();
            const translationCN =
                await this.translatorCN.queryProblemTranslationCN(
                    dailyChallenge.question.titleSlug
                );
            if (!translationCN) {
                throw new Error("Failed to fetch Chinese translation");
            }
            dailyChallenge.question.translatedTitle =
                translationCN?.data?.question?.translatedTitle || null;
            dailyChallenge.question.translatedContent =
                translationCN?.data?.question?.translatedContent || null;
            return dailyChallenge;
        } catch (error) {
            console.error(`Error fetching daily challenge:`, error);
            throw new Error("Failed to fetch daily challenge!");
        }
    }
    async getProblemTotalNumber(): Promise<number> {
        if (!this.leetCodeMetaData) {
            throw new Error("LeetCode data not loaded");
        }
        // if leetCodeMetaData is updated yesterday, then update the data again
        const today = new Date();
        const lastUpdated = new Date(this.leetCodeMetaData.last_updated);
        if (today.getDate() !== lastUpdated.getDate()) {
            this.leetCodeMetaData = await this.fetchProblemListMetaData();
            if (!this.leetCodeMetaData) {
                throw new Error("Failed to fetch problem list metadata");
            }
        }

        return this.leetCodeMetaData.num_total;
    }
    async fetchProblemListMetaData(): Promise<LeetCodeMetaData | null> {
        const API = "https://leetcode.com/api/problems/all/";
        try {
            const response = await fetch(API);
            if (!response.ok) {
                throw new Error("Failed to fetch problem list metadata");
            }
            const data = await response.json();
            data.last_updated = new Date().toISOString();
            // save the data to local file
            await fs.writeFile(
                path.join(__dirname, "../data/leetcode_data.json"),
                JSON.stringify(data, null, 2),
                "utf-8"
            );
            return data;
        } catch (error) {
            console.error("Error fetching problem list metadata:", error);
            return null;
        }
    }
}

export default ProblemService;
