# Data Sources

This project combines enzyme data with polymer chemistry data to study whether
sequence-based predictors can generalize across unseen enzyme families and new
polymer chemistries.

## Enzyme and organism sources

| Source | Information provided | Use in the project |
| --- | --- | --- |
| PAZy | Biochemically verified plastic-active enzymes | Primary source of positive enzyme records, particularly for PET and PUR degradation |
| PlasticDB | Reported enzymes, organisms and plastic-degradation information | Additional reported enzymes and organisms, and possible experimental negative evidence |
| PMBD | Further reported enzymes and organisms | Additional evidence and cross-checking of enzyme and organism annotations |
| UniProt | Amino acid sequences and protein metadata | Retrieval of protein sequences and accession-associated annotations |

PAZy contains 477 unique entries of biochemically verified plastic-active
enzymes. Its reported activities cover multiple polymers, with PET and PUR
among the relevant substrate groups for this project.

PlasticDB and PMBD provide further reported enzymes and organisms. They must be
used alongside their experimental substrate and assay information. A database
record or the absence of a database annotation is not sufficient to establish
that an enzyme is inactive.

## Polymer sources

The polymer side will be represented by repeat-unit chemistry:

* RDKit will generate interpretable repeat-unit descriptors from polymer
  structures.
* polyBERT may provide optional polymer embeddings as an alternative or
  additional representation.

Polymer structures must be selected and documented individually. PUR is a
polymer family with varied formulations and should not be represented by an
unsupported universal structure.

## UniProt sequences

UniProt should provide amino acid sequences for enzyme entries that have
corresponding accessions. Sequence records should be checked for:

* missing or incomplete sequences;
* internal whitespace and formatting;
* canonical amino acid symbols;
* sequence duplicates;
* consistency between the accession and the reported enzyme.

## Negative results

Negative labels require explicit evidence that an enzyme was tested against a
specific polymer and produced a negative assay result under documented
conditions. They must not be inferred from:

* activity reported for a different polymer;
* the absence of a substrate annotation;
* a missing record in another database;
* protein domains or catalytic motifs alone.

## Computational tools

| Tool | Purpose |
| --- | --- |
| MMseqs2 | Cluster enzymes by sequence similarity and create groups for held-out splits |
| RDKit | Calculate descriptors from validated polymer repeat-unit structures |
| polyBERT | Optionally represent polymer repeat units as embeddings |

MMseqs2 is a clustering tool, not a biological data source. Clusters should
keep all sequence members in the same training or held-out partition to reduce
homology leakage. The sequence identity and coverage thresholds used for
clustering must be reported.

The MMseqs2 groups are operational sequence-similarity clusters, not
necessarily established enzyme-family boundaries.
