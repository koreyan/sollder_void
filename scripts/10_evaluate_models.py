from ultralytics import YOLO
import json

def evaluate_models():
    print("--- 🚀 Starting Phase 4: Model Evaluation on Test Set ---")
    
    results_summary = {}

    # 1. Evaluate Baseline Model
    print("\n[1/2] Evaluating Baseline Model...")
    baseline_model = YOLO("runs/detect/models/detector/baseline-2/weights/best.pt")
    baseline_metrics = baseline_model.val(data="data/data.yaml", split="test", project="runs/detect/eval", name="baseline_test")
    
    results_summary["baseline"] = {
        "mAP50": baseline_metrics.box.map50,
        "mAP50-95": baseline_metrics.box.map,
        "Precision": baseline_metrics.box.mp,
        "Recall": baseline_metrics.box.mr,
        "F1": (2 * baseline_metrics.box.mp * baseline_metrics.box.mr) / (baseline_metrics.box.mp + baseline_metrics.box.mr) if (baseline_metrics.box.mp + baseline_metrics.box.mr) > 0 else 0
    }
    
    # 2. Evaluate Proposed Model
    print("\n[2/2] Evaluating Proposed Model...")
    proposed_model = YOLO("runs/detect/models/detector/proposed/weights/best.pt")
    proposed_metrics = proposed_model.val(data="data/data.yaml", split="test", project="runs/detect/eval", name="proposed_test")

    results_summary["proposed"] = {
        "mAP50": proposed_metrics.box.map50,
        "mAP50-95": proposed_metrics.box.map,
        "Precision": proposed_metrics.box.mp,
        "Recall": proposed_metrics.box.mr,
        "F1": (2 * proposed_metrics.box.mp * proposed_metrics.box.mr) / (proposed_metrics.box.mp + proposed_metrics.box.mr) if (proposed_metrics.box.mp + proposed_metrics.box.mr) > 0 else 0
    }

    # Print Summary
    print("\n=== 📊 Final Evaluation Results on Test Set ===")
    print(json.dumps(results_summary, indent=4))
    
    with open("eval_results.json", "w") as f:
        json.dump(results_summary, f, indent=4)
        
    print("✅ Results saved to eval_results.json")

if __name__ == "__main__":
    evaluate_models()
