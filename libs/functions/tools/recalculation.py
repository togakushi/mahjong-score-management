"""
libs/functions/tools/recalculation.py
"""

import logging
from contextlib import closing

import libs.global_value as g
from libs.domain import modify
from libs.domain.score import GameResult
from libs.utils import dbutil, dictutil


def main() -> None:
    """ポイント再計算"""
    g.cfg.initialization()

    target_rule: set[str] = set()
    for x in g.args.recalculation:
        if chk := g.cfg.rule.keyword_mapping.get(x):
            target_rule.add(chk)
        if x in g.cfg.rule.rule_list:
            target_rule.add(x)
    if not target_rule:
        target_rule.update(g.cfg.rule.rule_list)

    modify.db_backup()

    with closing(dbutil.connection(g.cfg.setting.database_file)) as cur:
        for rule_version in target_rule:
            print(rule_version)
            logging.info("%s", vars(g.cfg.rule.data.get(rule_version)))
            rows = cur.execute(
                """
                select
                    ts,
                    p1_name, p1_str,
                    p2_name, p2_str,
                    p3_name, p3_str,
                    p4_name, p4_str,
                    comment,
                    rule_version
                    from result where rule_version=?;
                """,
                (rule_version,),
            )
            count = 0

            for row in rows:
                dictutil.merge_dicts(dict(row), g.cfg.rule.to_dict(rule_version))
                result = GameResult(**dictutil.merge_dicts(dict(row), g.cfg.rule.to_dict(rule_version)))
                cur.execute(dbutil.query("RESULT_UPDATE"), result.to_dict())
                count += 1
            logging.info("recalculated: %s", count)

        cur.commit()
