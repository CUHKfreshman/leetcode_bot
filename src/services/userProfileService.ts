import { LeetCode, UserProfile } from 'leetcode-query';

class UserProfileService {
  private leetcode: LeetCode;

  constructor() {
    this.leetcode = new LeetCode();
  }

  async getUserProfile(username: string): Promise<UserProfile> {
    try {
      const user = await this.leetcode.user(username);
      return user;
    } catch (error) {
      console.error(`Error fetching user profile for ${username}:`, error);
      throw new Error('Failed to fetch user profile');
    }
  }
}

export default new UserProfileService();