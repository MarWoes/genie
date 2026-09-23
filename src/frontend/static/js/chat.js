function chat() {
    return {
        messages: [],
        input: "",
        loading: false,
        error: "",

        scrollToBottom() {
            this.$nextTick(() => {
                this.$refs.list.scrollTo({top: this.$refs.list.scrollHeight, behavior: "smooth"});
            });
        },

        async send() {

            this.loading = true;
            this.error = "";

            this.messages.push({role: "user", content: this.input});
            this.scrollToBottom();

            try {

                const response = await fetch("/chat", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({messages: this.messages}),

                });

                if (!response.ok) throw new Error("Chat request failed");

                const result = await response.json();
                this.messages = result.messages
                this.input = "";

            } catch {

                this.error = "Could not send message. Please try again.";

            } finally {

                this.loading = false;
                this.scrollToBottom();

            }
        },
    };
}
