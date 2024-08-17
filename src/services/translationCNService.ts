import {
    LeetCodeCN,
    LeetCodeGraphQLQuery,
    LeetCodeGraphQLResponse,
} from "leetcode-query";

class TranslationCNService {
    // leetcode-cn only has graphql API in this library
    private leetcodeCN: LeetCodeCN | null = null;
    constructor() {
        this.leetcodeCN = new LeetCodeCN();
    }
    async queryProblemTranslationCN(slug: string): Promise<LeetCodeGraphQLResponse | null> {
        if (!this.leetcodeCN) {
            throw new Error("LeetCode API not loaded");
        }
        try {
            // note that leetcode-cn only has graphql API in this library
            this.leetcodeCN = new LeetCodeCN();
            const query: LeetCodeGraphQLQuery = {
                operationName: "questionTranslations",
                variables: {
                    titleSlug: slug,
                },
                query: `query questionTranslations($titleSlug: String!) {
                            question(titleSlug: $titleSlug) {
                                translatedTitle
                                translatedContent
                            }
                    }
                `,
            };
            const problem = await this.leetcodeCN.graphql(query);
            return problem;
        } catch (error) {
            console.error("Error fetching problem details:", error);
            return null;
        }
    }
}

export default TranslationCNService;