# Publishing Notes

## Ready

The package contains:

- public-facing README;
- CVI Protocol 0.1;
- one-page Claim Card;
- Intervention Guide;
- Glossary;
- worked failed-certification case study;
- refreshed, non-exhaustive related-work note;
- conservative novelty matrix;
- historical provenance;
- pilot/KILLBOX evidence and raw archive;
- citation metadata (`CITATION.cff`);
- scoped public licensing (`LICENSE.md`).

## Licensing decision

The repository now uses scoped licensing rather than one blanket license:

- project-authored research and documentation: **CC BY 4.0**;
- code under `experiments/reference-implementation/`: **MIT**;
- preserved evidence and archives: included for transparency and reproducibility without an additional blanket grant where rights or terms may differ.

See `LICENSE.md` for the exact scope.

## Citation

Author name for citation: **Thom Finlayson**.

GitHub citation metadata is provided in `CITATION.cff`.

## Suggested release label

`CVI Protocol 0.1 — provisional public research artifact`

Suggested tag: `v0.1.0`

## Suggested repository description

> A provisional open protocol for testing whether bounded AI capability claims survive controlled feedback, retention boundaries, transfer, independent verification, and competing explanations.

## Claims to avoid in release copy

- “first causal AI evaluation framework”
- “proven theory of intelligence”
- “proves AI learns”
- “scientifically verified intelligence score”
- “the pilot validated CVI”

## Claims supported by the package

- the original project proposed a distinction between static performance and externally tested adaptive capability;
- an early adversarial exploration reframed the useful core as a credentialing protocol;
- an implemented pilot did not support a CVI result;
- a subsequent audit found concrete confounds and metric/control defects;
- CVI 0.1 incorporates those failures into a reusable experimental checklist;
- novelty of the complete protocol remains unresolved.

## Next publication step

Create a GitHub release tagged `v0.1.0` from the current `main` branch using the suggested release label above. After that release exists, it can be archived to Zenodo for a citable DOI snapshot.
