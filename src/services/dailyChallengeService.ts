import { LeetCode, DailyChallenge } from 'leetcode-query';
import TranslationCNService from './translationCNService';
class DailyChallengeService {
  private leetcode: LeetCode;
  private translatorCN: TranslationCNService;
  constructor() {
    this.leetcode = new LeetCode();
    this.translatorCN = new TranslationCNService();
  }

  async getDailyChallenge(): Promise<DailyChallenge> {
    try {
      const dailyChallenge = await this.leetcode.daily();
      const translationCN = await this.translatorCN.queryProblemTranslationCN(dailyChallenge.question.titleSlug);
      if (!translationCN) {
        throw new Error('Failed to fetch Chinese translation');
      }
      dailyChallenge.question.translatedTitle = translationCN?.data?.question?.translatedTitle || null;
      dailyChallenge.question.translatedContent = translationCN?.data?.question?.translatedContent || null;
      return dailyChallenge;
    } catch (error) {
      console.error(`Error fetching daily challenge:`, error);
      throw new Error('Failed to fetch daily challenge!');
    }
  }
}

export default new DailyChallengeService();