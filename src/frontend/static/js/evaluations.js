function evaluations() {
    return {
        cases: [],
        result: null,
        busy: false,
        error: "",

        async init() {
            try {
                const response = await fetch("/evaluations");
                if (!response.ok) throw new Error("Could not load evaluation cases.");
                const data = await response.json();
                this.cases = data.cases;
            } catch (error) {
                this.error = error.message;
            }
        },

        percent(value) {
            return `${(value * 100).toFixed(1)}%`;
        },

        async run() {
            this.busy = true;
            this.error = "";
            this.result = null;
            try {
                const response = await fetch("/evaluations/run", {method: "POST"});
                const data = await response.json();
                if (!response.ok) throw new Error(data.detail || "Evaluation failed.");
                this.result = data;
            } catch (error) {
                this.error = error.message;
            } finally {
                this.busy = false;
            }
        },
    };
}
