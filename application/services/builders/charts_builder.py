from pathlib import Path
import webbrowser
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA

class ChartsBuilder:
    def __init__(
        self, 
        output_dir: str = "reports"
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def _save_and_open(self, filename: str) -> Path:
        output_path = self.output_dir / filename

        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        webbrowser.open(output_path.resolve().as_uri())

        return output_path

    def clusters(
        self,
        embeddings,
        labels,
        filename: str = "clusters_visualization.png"
    ) -> Path:
        pca = PCA(n_components=2)
        points_2d = pca.fit_transform(embeddings)

        plt.figure(figsize=(10, 7))

        scatter = plt.scatter(
            points_2d[:, 0],
            points_2d[:, 1],
            c=labels,
            cmap="tab10",
            alpha=0.75
        )

        plt.title("Embedding clusters visualization")
        plt.xlabel("PCA component 1")
        plt.ylabel("PCA component 2")
        plt.colorbar(scatter, label="Cluster")
        plt.grid(True, alpha=0.3)

        return self._save_and_open(filename)

    def token_limit_bar(
        self,
        token_statistics: list[dict],
        filename: str = "token_limit_chart.png"
    ) -> Path:
        if not token_statistics:
            raise ValueError("Brak danych token_statistics")

        doc_ids = []
        token_counts = []
        max_tokens_values = []

        for item in token_statistics:
            doc_ids.append(str(item.get("doc_id")))
            token_counts.append(int(item.get("token_count", 0)))

            if item.get("max_tokens") is not None:
                max_tokens_values.append(int(item.get("max_tokens")))

        if not max_tokens_values:
            raise ValueError("Brak max_tokens w token_statistics")

        max_tokens = max(max_tokens_values)

        plt.figure(figsize=(12, 6))

        plt.bar(doc_ids, token_counts)

        plt.axhline(
            y=max_tokens,
            color="red",
            linestyle="--",
            linewidth=2,
            label=f"Max tokens: {max_tokens}"
        )

        plt.title("Document token count")
        plt.xlabel("Document ID")
        plt.ylabel("Token count")
        plt.legend()
        plt.grid(axis="y", alpha=0.3)
        plt.xticks(rotation=45)

        return self._save_and_open(filename)

    def cosine_similarity_progress(
        self,
        similarities: list[dict],
        filename: str = "cosine_similarity_progress.png"
    ) -> Path:
        labels = [
            str(item.get("label") or item.get("doc_id") or index + 1)
            for index, item in enumerate(similarities)
        ]

        values = [
            float(item["cosine_similarity"])
            for item in similarities
        ]

        y_positions = np.arange(len(labels))

        plt.figure(figsize=(10, 6))

        plt.barh(y_positions, values)

        plt.xlim(0, 1)
        plt.yticks(y_positions, labels)

        plt.title("Cosine similarity")
        plt.xlabel("Similarity score")
        plt.ylabel("Document")
        plt.grid(axis="x", alpha=0.3)

        for index, value in enumerate(values):
            plt.text(
                value + 0.01,
                index,
                f"{value:.2f}",
                va="center"
            )

        return self._save_and_open(filename)