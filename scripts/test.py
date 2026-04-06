import os
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
import warnings
warnings.filterwarnings('ignore')

# Data processing
import pandas as pd
import numpy as np

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("Core imports loaded successfully!")

# ML/AI imports (load when needed to save memory)
def load_ml_dependencies():
    """Lazy load ML dependencies."""
    global torch, whisper, transformers
    import torch
    import whisper
    import transformers
    
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    return torch, whisper, transformers

torch, whisper, transformers = load_ml_dependencies()

@dataclass
class ProjectConfig:
    """Central configuration for the AI Content Development project."""
    
    # Project metadata
    project_name: str = "ASML AI Content Development"
    version: str = "0.1.0"
    
    # Paths
    data_dir: Path = Path("./Data/Test")
    raw_videos_dir: Path = Path("./Data/raw_videos")
    processed_dir: Path = Path("./Data/processed")
    transcripts_dir: Path = Path("./Data/transcripts")
    embeddings_dir: Path = Path("./Data/embeddings")
    output_dir: Path = Path("./output")
    models_dir: Path = Path("./models")
    logs_dir: Path = Path("./logs")
    
    # ASR Configuration
    whisper_model: str = "large-v3"  # Options: tiny, base, small, medium, large, large-v2, large-v3
    whisper_language: str = "en"
    
    # LLM Configuration
    llm_model: str = "gpt-4"  # Or local model path
    llm_temperature: float = 0.1
    llm_max_tokens: int = 4096
    
    # Embedding Configuration
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Video Processing
    target_clip_duration: Tuple[int, int] = (60, 120)  # 1-2 minutes in seconds
    video_fps: int = 30
    
    # Retrieval Configuration
    top_k_retrieval: int = 5
    similarity_threshold: float = 0.7
    
    def __post_init__(self):
        """Create necessary directories."""
        for path_attr in ['data_dir', 'raw_videos_dir', 'processed_dir', 
                          'transcripts_dir', 'embeddings_dir', 'output_dir', 
                          'models_dir', 'logs_dir']:
            path = getattr(self, path_attr)
            path.mkdir(parents=True, exist_ok=True)
            
    def save(self, filepath: str = "config.json"):
        """Save configuration to JSON."""
        config_dict = {
            k: str(v) if isinstance(v, Path) else v 
            for k, v in self.__dict__.items()
        }
        with open(filepath, 'w') as f:
            json.dump(config_dict, f, indent=2)
            
    @classmethod
    def load(cls, filepath: str = "config.json"):
        """Load configuration from JSON."""
        with open(filepath, 'r') as f:
            config_dict = json.load(f)
        return cls(**config_dict)

# Initialize configuration
config = ProjectConfig()
config.save()
print(f"Project '{config.project_name}' initialized successfully!")
print(f"Data directory: {config.data_dir.absolute()}")

@dataclass
class TranscriptSegment:
    """Represents a segment of transcribed audio with timestamps."""
    text: str
    start_time: float  # seconds
    end_time: float    # seconds
    confidence: float = 1.0
    speaker: Optional[str] = None
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time
    
    def to_dict(self) -> Dict:
        return {
            'text': self.text,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'confidence': self.confidence,
            'speaker': self.speaker
        }

@dataclass 
class VideoMetadata:
    """Metadata for a training video."""
    video_id: str
    title: str
    filepath: Path
    duration: float  # seconds
    topics: List[str] = field(default_factory=list)
    machine_types: List[str] = field(default_factory=list)
    error_codes: List[str] = field(default_factory=list)
    safety_notes: List[str] = field(default_factory=list)
    created_date: Optional[datetime] = None
    
@dataclass
class InstructionalSegment:
    """A semantically meaningful instructional segment."""
    segment_id: str
    video_id: str
    title: str
    summary: str
    start_time: float
    end_time: float
    transcript_segments: List[TranscriptSegment]
    steps: List[str] = field(default_factory=list)
    tools_required: List[str] = field(default_factory=list)
    safety_warnings: List[str] = field(default_factory=list)
    relevance_score: float = 0.0
    embedding: Optional[np.ndarray] = None
    
@dataclass
class MicroClip:
    """A generated micro-clip for troubleshooting."""
    clip_id: str
    query: str
    source_segments: List[InstructionalSegment]
    output_path: Optional[Path] = None
    total_duration: float = 0.0
    captions: List[Dict] = field(default_factory=list)
    safety_validated: bool = False
    validation_notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)

print("Data structures defined successfully!")

class VideoDataLoader:
    """Handles loading and basic processing of training videos."""
    
    def __init__(self, config: ProjectConfig):
        self.config = config
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        
    def scan_videos(self) -> List[VideoMetadata]:
        """Scan the raw videos directory and catalog all videos."""
        videos = []
        
        for video_path in self.config.raw_videos_dir.glob('**/*'):
            if video_path.suffix.lower() in self.supported_formats:
                metadata = self._extract_metadata(video_path)
                videos.append(metadata)
                
        logger.info(f"Found {len(videos)} videos in {self.config.raw_videos_dir}")
        return videos
    
    def _extract_metadata(self, video_path: Path) -> VideoMetadata:
        """Extract metadata from a video file."""
        # TODO: Implement actual metadata extraction using moviepy/ffprobe
        return VideoMetadata(
            video_id=video_path.stem,
            title=video_path.stem.replace('_', ' ').title(),
            filepath=video_path,
            duration=0.0,  # Will be populated by actual extraction
            topics=[],
            machine_types=[],
            error_codes=[]
        )
    
    def get_video_stats(self, videos: List[VideoMetadata]) -> pd.DataFrame:
        """Generate statistics about the video corpus."""
        stats = []
        for v in videos:
            stats.append({
                'video_id': v.video_id,
                'title': v.title,
                'duration_min': v.duration / 60,
                'num_topics': len(v.topics),
                'num_error_codes': len(v.error_codes)
            })
        return pd.DataFrame(stats)

# Initialize data loader
data_loader = VideoDataLoader(config)

# Scan for videos (will be empty until data is added)
videos = data_loader.scan_videos()
print(f"Loaded {len(videos)} videos")

class ASRPipeline:
    """Automatic Speech Recognition pipeline using Whisper."""
    
    def __init__(self, config: ProjectConfig):
        self.config = config
        self.model = None
        
    def load_model(self):
        """Load the Whisper model."""
        import whisper
        logger.info(f"Loading Whisper model: {self.config.whisper_model}")
        self.model = whisper.load_model(self.config.whisper_model)
        logger.info("Model loaded successfully")
        
    def transcribe(self, video_path: Path, 
                   word_timestamps: bool = True) -> List[TranscriptSegment]:
        """Transcribe a video file and return segments with timestamps."""
        if self.model is None:
            self.load_model()
            
        logger.info(f"Transcribing: {video_path.name}")
        
        # Transcribe with word-level timestamps
        result = self.model.transcribe(
            str(video_path),
            language=self.config.whisper_language,
            word_timestamps=word_timestamps,
            verbose=False
        )
        
        # Convert to TranscriptSegment objects
        segments = []
        for seg in result['segments']:
            segments.append(TranscriptSegment(
                text=seg['text'].strip(),
                start_time=seg['start'],
                end_time=seg['end'],
                confidence=seg.get('confidence', 1.0)
            ))
            
        logger.info(f"Transcribed {len(segments)} segments")
        return segments
    
    def save_transcript(self, segments: List[TranscriptSegment], 
                        video_id: str) -> Path:
        """Save transcript to JSON file."""
        output_path = self.config.transcripts_dir / f"{video_id}_transcript.json"
        
        data = {
            'video_id': video_id,
            'created_at': datetime.now().isoformat(),
            'num_segments': len(segments),
            'segments': [seg.to_dict() for seg in segments]
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
            
        logger.info(f"Saved transcript to {output_path}")
        return output_path

# Initialize ASR pipeline
asr_pipeline = ASRPipeline(config)
print("ASR Pipeline initialized (model not loaded yet)")

# Transcribe a video
video_path = config.raw_videos_dir / "Unscheduled downs_The Unhappy Flow.mp4"
if video_path.exists():
    segments = asr_pipeline.transcribe(video_path)
    asr_pipeline.save_transcript(segments, "Unscheduled downs_The Unhappy Flow")
    
    # Display first few segments
    for i, seg in enumerate(segments[:5]):
        print(f"[{seg.start_time:.2f}s - {seg.end_time:.2f}s] {seg.text}")