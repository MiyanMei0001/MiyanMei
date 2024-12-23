class TikWm {
    constructor(jsonData) {
        if (!jsonData?.data?.videos) {
            throw new Error('Invalid JSON data structure');
        }
        this.videos = jsonData.data.videos;
    }

    getTotalVideos() {
        return this.videos.length;
    }

    getRandomVideo() {
        try {
            if (this.videos.length === 0) {
                throw new Error('No videos available');
            }

            const randomIndex = Math.floor(Math.random() * this.videos.length);
            const randomVideo = this.videos[randomIndex];

            return {
                index: randomIndex,
                total_videos: this.videos.length,
                video_id: randomVideo.video_id,
                title: randomVideo.title,
                play: randomVideo.play,
                duration: randomVideo.duration,
                play_count: randomVideo.play_count,
                author: randomVideo.author.nickname,
                create_time: randomVideo.create_time,
                region: randomVideo.region
            };
        } catch (error) {
            console.error('Error getting random video:', error.message);
            return null;
        }
    }

    getMultipleRandomVideos(count) {
        try {
            if (this.videos.length === 0) {
                throw new Error('No videos available');
            }

            // Ensure count doesn't exceed total videos
            count = Math.min(count, this.videos.length);
            
            // Create copy of indices and shuffle them
            const indices = Array.from({ length: this.videos.length }, (_, i) => i);
            for (let i = indices.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [indices[i], indices[j]] = [indices[j], indices[i]];
            }
            
            // Get the specified number of random videos
            return indices.slice(0, count).map(index => ({
                index: index,
                total_videos: this.videos.length,
                video_id: this.videos[index].video_id,
                title: this.videos[index].title,
                play: this.videos[index].play,
                duration: this.videos[index].duration,
                play_count: this.videos[index].play_count,
                author: this.videos[index].author.nickname,
                create_time: this.videos[index].create_time,
                region: this.videos[index].region
            }));
        } catch (error) {
            console.error('Error getting multiple random videos:', error.message);
            return [];
        }
    }

    getFirstVideo() {
        try {
            if (this.videos.length === 0) {
                throw new Error('No videos available');
            }

            const firstVideo = this.videos[0];
            return {
                video_id: firstVideo.video_id,
                title: firstVideo.title,
                play: firstVideo.play,
                duration: firstVideo.duration,
                play_count: firstVideo.play_count,
                author: firstVideo.author.nickname,
                create_time: firstVideo.create_time,
                region: firstVideo.region
            };
        } catch (error) {
            console.error('Error getting first video:', error.message);
            return null;
        }
    }
}

module.exports = TikWm;