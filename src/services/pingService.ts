class PingService {
  async getPongResponse(): Promise<string> {
    // Simulate a complex operation
    await new Promise(resolve => setTimeout(resolve, 100));
    return 'pong';
  }
}

export default new PingService();