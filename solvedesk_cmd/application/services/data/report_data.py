import numpy as np
import matplotlib.pyplot as plt
import webbrowser

from pathlib import Path
from collections import Counter
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity

class DataReporter:
    def __init__(
        self,
        model,
        documents: list[str],
        embeddings: list,
        clusters: int = 3
    ):
        self.model = model
        self.documents = documents
        self.embeddings = np.array(embeddings)
        self.clusters = clusters
        self.labels = None

    def execute(self) -> dict:
        mean_similarity = self.get_similarity()
        clusters_report = self.get_clusters()
        token_report = self.token_statistics()

        report = {
            "documents_count": len(self.documents),
            "embedding_size": len(self.embeddings[0]) if len(self.embeddings) > 0 else 0,
            "mean_similarity": mean_similarity,
            "labels": self.labels,
            "clusters": clusters_report,
            "token_statistics": token_report
        }

        return report

    def get_similarity(self) -> float:
        similarity_matrix = cosine_similarity(self.embeddings)
        mean_similarity = similarity_matrix.mean()

        return float(mean_similarity)

    def get_clusters(self) -> list[dict]:
        kmeans = KMeans(
            n_clusters=self.clusters,
            random_state=42,
            n_init="auto"
        )

        self.labels = kmeans.fit_predict(self.embeddings)

        cluster_counts = Counter(self.labels)

        clusters_list = []

        for cluster_id, count in cluster_counts.items():
            item = {
                "cluster_id": int(cluster_id),
                "count": int(count)
            }

            clusters_list.append(item)

        return clusters_list

    def token_statistics(self) -> list[dict]:
        statistics = []

        max_tokens = self.model.max_seq_length

        for i, (doc, emb) in enumerate(zip(self.documents, self.embeddings)):
            tokens = self.model.tokenize([str(doc)])

            token_count = len(tokens["input_ids"][0])

            usage_percent = round(
                token_count / max_tokens * 100,
                2
            )

            item = {
                "doc_id": i + 1,
                "token_count": token_count,
                "max_tokens": max_tokens,
                "usage_percent": usage_percent,
                "truncated": token_count >= max_tokens,
                "embedding_size": len(emb)
            }

            statistics.append(item)

        return statistics

    def get_visualization(self) -> bool:
        try:
            if self.labels is None:
                self.get_clusters()

            pca = PCA(n_components=2)
            points_2d = pca.fit_transform(self.embeddings)

            output_dir = Path("reports")
            output_dir.mkdir(exist_ok=True)

            output_path = output_dir / "clusters_visualization.png"

            plt.figure(figsize=(10, 7))

            scatter = plt.scatter(
                points_2d[:, 0],
                points_2d[:, 1],
                c=self.labels,
                cmap="tab10",
                alpha=0.75
            )

            plt.title("Embedding clusters visualization")
            plt.xlabel("PCA component 1")
            plt.ylabel("PCA component 2")
            plt.colorbar(scatter, label="Cluster")
            plt.grid(True, alpha=0.3)

            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            plt.close()

            webbrowser.open(output_path.resolve().as_uri())

            return True

        except Exception:
            return False