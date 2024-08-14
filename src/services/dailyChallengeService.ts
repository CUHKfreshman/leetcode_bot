import { LeetCode, DailyChallenge } from 'leetcode-query';

class DailyChallengeService {
  private leetcode: LeetCode;

  constructor() {
    this.leetcode = new LeetCode();
  }

  async getDailyChallenge(): Promise<DailyChallenge> {
    try {
      const dailyChallenge = await this.leetcode.daily();
      return dailyChallenge;
    } catch (error) {
      console.error(`Error fetching daily challenge:`, error);
      throw new Error('Failed to fetch daily challenge!');
    }
  }
}

export default new DailyChallengeService();