# UI Architecture

## Globe Navigation Model
**Added: 2026-04-07 | Revised: 2026-04-09**

The primary navigation metaphor for the user interface is an interactive globe. Knowledge domains appear as regions on the surface, but their spatial arrangement is determined by graph topology — concepts that are connected by prerequisite edges are placed near each other — not by categorical labels. Zooming into a region reveals finer structure; zooming further reveals individual concept nodes and the edges between them.

Mastery states are visible in the surface: unvisited territory is dark; exposed nodes have dim ambient light; proficiency illuminates a node clearly; mastery causes it to glow and activates its tendrils. The globe is the trophy as well as the map — the learner's intellectual territory made visible over time.

This navigation model sits above the syllabus architecture, not in place of it. The globe is the home screen; the syllabus is the committed working mode within it. A user taps a concept on the globe, sees a card with prerequisites and mastery state, and commits to study — which generates or resumes a syllabus. Active syllabi (max five, hard cap) are shown as colored trails with destination markers. Completed syllabi leave no trail — mastery glow on the nodes is the only persistent record. Full interaction design in session-lifecycle.md.

## Level-of-Detail Rendering
**Added: 2026-04-09**

At scale (hundreds to thousands of nodes across domains), the globe cannot render every node individually at all zoom levels. Level-of-detail (LOD) rendering aggregates nearby nodes into clusters at zoomed-out views and fractures them into individual nodes as the user zooms in.

**Clustering is computed from edge topology, not from domain categories.** Community detection algorithms (Louvain, Leiden) identify densely connected subgraphs and produce a hierarchy of clusters at multiple resolutions. These clusters reflect genuine intellectual proximity — concepts that share many prerequisite relationships cluster together. The groupings are emergent from the graph's actual structure, which means they shift when the graph changes (new edges added, nodes split). The computation is cheap at projected scale (near-linear time) and can be recomputed on any graph edit, cached until the next.

**Domain tags provide color and filtering, not spatial grouping.** Each node carries a `domain TEXT[]` tag (see architecture.md, Node Schema). These tags are flat labels — no hierarchy, no enforced taxonomy. The globe renders domain membership as node color, and the UI can filter by domain tag. But domain tags do not determine where a node is placed on the globe surface, and they do not define the cluster boundaries at any zoom level. A concept tagged `['ethics', 'epistemology']` is placed where its edges put it, not in an "ethics region" or an "epistemology region."

**Zoom behavior.** Zoomed fully out, the user sees a small number of high-level clusters (perhaps 5–12, depending on graph density and community detection output). Each cluster shows a summary: dominant domain color, number of nodes, the user's aggregate mastery within the cluster. Zooming in fractures a cluster into sub-clusters or individual nodes. Zooming further reveals edges between nodes and the learner's specific mastery state per node. The transition is continuous, not discrete — no hard zoom "levels" with sudden transitions.

**No spatial data on nodes.** Globe position is computed by a force-directed or topological layout algorithm from edge structure and community detection output. Positions are not stored in the node table. This means every graph edit potentially shifts positions, which is correct — the map should reflect the current graph, not a manually curated layout.

**Cross-domain tendrils.** When a concept reaches mastery, its tendrils — connections to concepts in distant parts of the globe — become visible. These are edges that cross community detection boundaries: prerequisite relationships that link concepts which the clustering algorithm placed far apart. Tendrils are the globe's way of showing the learner that mastering one idea opens paths to seemingly unrelated territory.

---
*Last updated: 2026-04-09 (new file; globe model split from architecture.md; LOD rendering and community detection added)*
