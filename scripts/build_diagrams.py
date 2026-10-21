#!/usr/bin/env python3
"""Rebuild the course's editable vector diagrams for HTML and LaTeX/PDF."""
from pathlib import Path
import os
import textwrap

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "_build/matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = ROOT / "docs/_static/diagrams"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "svg.fonttype": "path", "pdf.fonttype": 42,
                     "svg.hashsalt": "statistical-learning-diagrams"})
COLORS = {"core": ("#9B1B68", "#FBEAF4"),
          "method": ("#176B72", "#EAF5F5"),
          "boundary": ("#966400", "#FFF6DD")}


def canvas(height):
    fig, ax = plt.subplots(figsize=(6.4, height))
    fig.subplots_adjust(0, 0, 1, 1)
    ax.set(xlim=(0, 6.4), ylim=(0, height))
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, title, body, kind="method"):
    edge, fill = COLORS[kind]
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.018,rounding_size=.07",
                              linewidth=1.2, facecolor=fill, edgecolor=edge))
    ax.text(x + .14, y + h - .22, title, color=edge, weight="bold", size=10.2, va="top")
    lines = "\n".join(textwrap.fill(p, max(20, int(w * 12))) for p in body.split("\n"))
    ax.text(x + .14, y + h - .53, lines, color="#243345", size=9.5,
            va="top", linespacing=1.45)


def arrow(ax, start, end, label=None, bend=None):
    patch = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=11,
                           linewidth=1.2, color="#526474",
                           connectionstyle=bend or "arc3,rad=0")
    ax.add_patch(patch)
    if label:
        ax.text((start[0]+end[0])/2, (start[1]+end[1])/2+.07, label,
                size=8.5, ha="center", va="bottom", color="#526474",
                bbox={"facecolor":"white", "edgecolor":"none", "pad":1})


def save(fig, name):
    for ext in ("svg", "pdf"):
        meta = {"Date": None} if ext == "svg" else {"CreationDate": None, "ModDate": None}
        fig.savefig(OUT / f"{name}.{ext}", facecolor="white", metadata=meta)
    plt.close(fig)


def four_steps(name, steps, footer=None, loop=False):
    fig, ax = canvas(4.25 if footer else 3.7)
    y0 = .85 if footer else .30
    coords = [(.20,y0+1.75), (3.45,y0+1.75), (3.45,y0), (.20,y0)]
    for (x,y), (title,body,kind) in zip(coords,steps):
        box(ax,x,y,2.75,1.25,title,body,kind)
    arrow(ax,(2.97,y0+2.37),(3.42,y0+2.37))
    arrow(ax,(4.82,y0+1.73),(4.82,y0+1.28))
    arrow(ax,(3.42,y0+.62),(2.98,y0+.62))
    if loop:
        arrow(ax,(1.57,y0+1.28),(1.57,y0+1.73))
        ax.text(1.72,y0+1.5,"next round",size=8.5,va="center",color="#526474")
    if footer:ax.text(.22,.36,footer,size=9.1,color="#526474",va="center")
    save(fig,name)


four_steps("course-map",[
    ("1  Define the target","Prediction risk, a preference contrast, regret, or a selected hypothesis?","core"),
    ("2  Describe observations","Which labels, comparisons, feedback, or selection decisions are recorded?","method"),
    ("3  State assumptions","Which mechanism identifies the target and supports the calculation?","boundary"),
    ("4  Match the evaluation","Measure the stated target; challenge one assumption at a time.","method")])

fig,ax=canvas(4.75)
box(ax,.2,3.5,2.75,1.05,"PU observations","Representative positives + full target marginal","core")
box(ax,3.45,3.5,2.75,1.05,"UU observations","Two mixtures; known, different class proportions","core")
box(ax,.2,1.95,2.75,1.05,"Check the mechanism","Verify the target prior and sampling from the full marginal","boundary")
box(ax,3.45,1.95,2.75,1.05,"Check the inverse","Shared class distributions; check prior gap and target prior.","boundary")
arrow(ax,(1.57,3.46),(1.57,3.03));arrow(ax,(4.82,3.46),(4.82,3.03))
box(ax,1.05,.28,4.3,1.05,"Rewrite risk, then evaluate","Estimate observable expectations; evaluate fitted rules with a justified assessment design.","method")
arrow(ax,(1.57,1.91),(2.2,1.37));arrow(ax,(4.82,1.91),(4.2,1.37))
save(fig,"weak-supervision")

four_steps("preference-design",[
    ("1  Choose the estimand","A contrast, pairwise probability, or ranking for a defined population","core"),
    ("2  Inspect the design","Comparison connectivity, feature variation, and repeated judges","boundary"),
    ("3  Fit and diagnose","Normalize strengths; inspect separation and dependence.","method"),
    ("4  Evaluate that target","Use relevant held-out units and the uncertainty measure the target needs.","method")])

four_steps("online-protocol",[
    ("1  Available history","Only information revealed before round t may inform the action.","boundary"),
    ("2  Act","Choose a decision or a distribution over actions.","core"),
    ("3  Receive feedback","Full information: all losses. Bandit: chosen reward only.","method"),
    ("4  Update","Use the permitted feedback and evaluate against a declared comparator.","method")],loop=True)

four_steps("bandit-loop",[
    ("1  Store observations","Arm counts and reward sums from completed rounds","method"),
    ("2  Choose one arm","For UCB: empirical mean + an exploration bonus","core"),
    ("3  Observe one reward","The policy does not see unchosen rewards or the true means.","boundary"),
    ("4  Update that arm","Increase its count and reward sum; leave other arms unchanged.","method")],
    footer="Simulation evaluator only: true means give pseudo-regret.\nThey are never passed into the policy's choice rule.",loop=True)

fig,ax=canvas(5.8)
box(ax,.6,4.7,5.2,.88,"1  Specify model and analysis choices","Account for features, noise, tuning, and pair selection.","boundary")
box(ax,.6,3.42,5.2,.88,"2  Run selection and define the target","Record the selected groups and the mean contrast to be tested.","core")
box(ax,.2,1.97,2.75,1.0,"Hierarchical clustering","Preserve the selected groups under the specified linkage.","method")
box(ax,3.45,1.97,2.75,1.0,"Path-conditioned k-means","Preserve the intermediate assignment history.","method")
box(ax,.6,.27,5.2,1.05,"3  Build the reference distribution","Fix nuisance information, find admissible radii, and integrate the truncated null tail.","method")
arrow(ax,(3.2,4.65),(3.2,4.34));arrow(ax,(2.0,3.38),(1.57,3.01));arrow(ax,(4.4,3.38),(4.82,3.01))
arrow(ax,(1.57,1.93),(2.1,1.36));arrow(ax,(4.82,1.93),(4.3,1.36))
save(fig,"selection-pipeline")

fig,ax=canvas(4.7)
box(ax,1,3.48,4.4,1.0,"Known-variance Gaussian construction","Observed X plus independent noise E with the same known covariance","boundary")
box(ax,.2,1.87,2.75,1.05,"Discovery component","Form X + E; use it to choose the groups and contrast.","core")
box(ax,3.45,1.87,2.75,1.05,"Inference component","Form X - E; reserve it for the stated contrast.","method")
box(ax,1,.22,4.4,1.02,"Condition on discovery, then infer","Groups are fixed given discovery; inference variance is doubled in this equal split.","method")
arrow(ax,(2.2,3.44),(1.57,2.96));arrow(ax,(4.2,3.44),(4.82,2.96))
arrow(ax,(1.57,1.83),(2.2,1.28));arrow(ax,(4.82,1.83),(4.2,1.28))
save(fig,"independent-information")
print("Built seven SVG/PDF diagram pairs.")
