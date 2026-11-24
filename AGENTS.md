# VNUK Observatory

This repository contains the VNUK token observatory generated from TON Observatory Template 1.2.0. Initial template commit is retained in Git history.

Use project.json for this token. Preserve verified contract, pool identity and branding. No foreign-token custom badges or invented data. Service labels use Tonkeeper first, supplemented with on-chain proof and provenance.

DeDust low-level direct swap parsing lives in dedust_native.py and must fail closed for failed, routed or ambiguous calls. Keep its real-response and rejection tests.

Before publishing changes run Python tests, Node tests, build.py and verify.py. Verify final desktop/mobile HTML, RU/EN, links, buttons, charts, badges, top 10/20 and no overflow or external rendering dependencies.

Preserve last-good snapshots, incomplete-source states and the current branch history. Never force push. Distinguish source saved, HTML checked, Actions run verified and TON Storage publication. Keep README descriptions attributed, contract-matched and sourced. Do not modify other observatories or the shared Cloudflare runner without a separate request.
