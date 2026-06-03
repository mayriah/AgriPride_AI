class RankEngine:
    def __init__(self):
        self.max_outputs = 3
        self.uncertainty_threshold = 0.7
        self.volatility_threshold = 0.2

    def validate_scout_output(self, data):
        if data.get("uncertainty", 0) > self.uncertainty_threshold:
            return "ESCALATE_GUARDIAN"
        
        if data.get("volatility", 0) > self.volatility_threshold:
            return "ESCALATE_HUNT"
        
        return "ALLOW"

    def enforce_output_limit(self, outputs):
        return outputs[:self.max_outputs]