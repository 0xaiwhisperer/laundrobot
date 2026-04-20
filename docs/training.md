# Training Models on Laundrobot Data

Laundrobot records datasets in the LeRobot format, which is directly compatible with all LeRobot training recipes.

## Dataset format

Each episode is stored as:
- A Parquet file containing joint positions, actions, timestamps, and language instructions
- MP4 video files for each camera stream

The dataset metadata follows the [LeRobot dataset spec](https://github.com/huggingface/lerobot/blob/main/docs/datasets.md).

## Training ACT

[ACT (Action Chunking with Transformers)](https://github.com/tonyzhaozh/act) is a strong baseline for manipulation.

```bash
# After pushing your dataset to HuggingFace Hub:
python -m lerobot.scripts.train \
  policy=act \
  dataset_repo_id=your-username/laundrobot-folding \
  env=aloha \
  training.num_workers=4 \
  training.batch_size=8 \
  training.num_train_steps=80000 \
  wandb.enable=true
```

## Training Diffusion Policy

```bash
python -m lerobot.scripts.train \
  policy=diffusion \
  dataset_repo_id=your-username/laundrobot-folding \
  training.batch_size=64 \
  training.num_train_steps=200000
```

## Evaluating with FAISS retrieval

FAISS retrieval doesn't require training — it plays back the most visually similar episode from your dataset directly on the robot. See [FAISS Retrieval](../README.md#-faiss-retrieval) in the main README.

## Dataset tips

| Goal | Recommendation |
|---|---|
| Minimum episodes | 50 for simple pick-and-place |
| Better generalization | 200+ with varied object positions |
| FPS | 30fps for fast motions; 10fps is fine for slow tasks |
| Scene resets | Reset to same start config ± a few cm of variation |
| Language instructions | Be specific: "Pick up the blue cup and place it in the white bowl" |

## Visualizing your dataset

```bash
# View a dataset in the LeRobot visualizer
python -m lerobot.scripts.visualize_dataset \
  --repo-id your-username/laundrobot-folding \
  --episode-index 0
```

## Checking data quality

```bash
# Print dataset statistics
python -c "
from lerobot.common.datasets.lerobot_dataset import LeRobotDataset
ds = LeRobotDataset('your-username/laundrobot-folding')
print(ds)
print('Episodes:', ds.num_episodes)
print('Frames:',   ds.num_frames)
"
```
