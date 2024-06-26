# -*- coding: utf-8 -*-

# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see LICENSE for details)
#  https://github.com/spyder-ide/three-merge
"""Main three_merge function."""

# Third-party imports
from diff_match_patch import diff_match_patch

# Constants
DIFFER = diff_match_patch()
PRESERVED = 0
DELETION = -1
ADDITION = 1


def merge(source: str, target: str, base: str) -> tuple[str, bool]:
    has_conflict = False
    diff1_l = DIFFER.diff_main(base, source)
    diff2_l = DIFFER.diff_main(base, target)

    diff1 = iter(diff1_l)
    diff2 = iter(diff2_l)

    composed_text = []
    source = next(diff1, None)
    target = next(diff2, None)

    while source is not None and target is not None:
        source_status, source_text = source
        target_status, target_text = target
        if source_status == PRESERVED and target_status == PRESERVED:
            # Base is preserved for both source and target
            if len(source_text) > len(target_text):
                # Addition performed by target
                advance = True
                composed_text.append(target_text)
                _, (_, invariant) = DIFFER.diff_main(target_text, source_text)
                target = next(diff2, None)
                while invariant != '' and target is not None:
                    # Apply target changes until invariant is preserved
                    # target = next(diff2, None)
                    target_status, target_text = target
                    if target_status == DELETION:
                        if len(target_text) > len(invariant):
                            target_text = target_text[len(invariant):]
                            invariant = ''
                            target = (target_status, target_text)
                        else:
                            invariant = invariant[len(target_text):]
                            target = next(diff2, None)
                    elif target_status == ADDITION:
                        composed_text.append(target_text)
                        target = next(diff2, None)
                    else:
                        # Recompute invariant and advance source
                        if len(invariant) > len(target_text):
                            assert invariant[:len(target_text)] == target_text
                            source = (
                                source_status, invariant[len(target_text):])
                            composed_text.append(target_text)
                            invariant = ''
                            advance = False
                            target = next(diff2, None)
                        else:
                            target_text = target_text[len(invariant):]
                            composed_text.append(invariant)
                            invariant = ''
                            target = (target_status, target_text)
                if advance:
                    source = next(diff1, None)
            elif len(source_text) < len(target_text):
                # Addition performed by source
                advance = True
                composed_text.append(source_text)
                _, (_, invariant) = DIFFER.diff_main(source_text, target_text)
                source = next(diff1, None)
                while invariant != '' and target is not None:
                    # Apply source changes until invariant is preserved
                    source_status, source_text = source
                    if source_status == DELETION:
                        if len(source_text) > len(invariant):
                            source_text = source_text[len(invariant):]
                            invariant = ''
                            source = (source_status, source_text)
                        else:
                            invariant = invariant[len(source_text):]
                            source = next(diff1, None)
                    elif source_status == ADDITION:
                        composed_text.append(source_text)
                        source = next(diff1, None)
                    else:
                        # Recompute invariant and advance source
                        # invariant = invariant[:len(source_text)]
                        if len(invariant) > len(source_text):
                            assert invariant[:len(source_text)] == source_text
                            target = (
                                target_status, invariant[len(source_text):])
                            composed_text.append(source_text)
                            invariant = ''
                            advance = False
                            source = next(diff1, None)
                        else:
                            source_text = source_text[len(invariant):]
                            composed_text.append(invariant)
                            invariant = ''
                            source = (source_status, source_text)
                if advance:
                    target = next(diff2, None)
            else:
                # Source and target are equal
                composed_text.append(source_text)
                source = next(diff1, None)
                target = next(diff2, None)
        elif source_status == ADDITION and target_status == PRESERVED:
            # Source is adding text
            composed_text.append(source_text)
            source = next(diff1, None)
        elif source_status == PRESERVED and target_status == ADDITION:
            # Target is adding text
            composed_text.append(target_text)
            target = next(diff2, None)
        elif source_status == DELETION and target_status == PRESERVED:
            if len(target_text) > len(source_text):
                # Take target text, remove the corresponding part from source
                target_text = target_text[len(source_text):]
                # composed_text.append(target_text)
                # source = diff1.pop(0)
                target = (target_status, target_text)
                source = next(diff1, None)
            elif len(target_text) < len(source_text):
                source_text = source_text[len(target_text):]
                source = (source_status, source_text)
                target = next(diff2, None)
        elif source_status == PRESERVED and target_status == DELETION:
            if len(source_text) > len(target_text):
                # Take source text, remove the corresponding part from target
                source_text = source_text[len(target_text):]
                source = (source_status, source_text)
                target = next(diff2, None)
            elif len(source_text) < len(target_text):
                # Advance to next source
                target_text = target_text[len(source_text):]
                target = (target_status, target_text)
                source = next(diff1, None)
        elif source_status == DELETION and target_status == ADDITION:
            # Merge conflict
            composed_text.append('<<<<<<< ++ {0} '.format(target_text))
            composed_text.append('======= -- {0} '.format(source_text))
            composed_text.append('>>>>>>>')
            has_conflict = True
            source = next(diff1, None)
            target = next(diff2, None)
            if target is not None:
                target_status, target_text = target
                if target_text.startswith(source_text):
                    target_text = target_text[len(source_text):]
                    target = (target_status, target_text)
        elif source_status == ADDITION and target_status == DELETION:
            # Merge conflict
            composed_text.append('<<<<<<< ++ {0} '.format(source_text))
            composed_text.append('======= -- {0} '.format(target_text))
            composed_text.append('>>>>>>>')
            has_conflict = True
            source = next(diff1, None)
            target = next(diff2, None)
            if source is not None:
                source_status, source_text = source
                if source_text.startswith(target_text):
                    source_text = source_text[len(target_text):]
                    source = (source_status, source_text)
        elif source_status == ADDITION and target_status == ADDITION:
            # Possible merge conflict
            if len(source_text) >= len(target_text):
                if source_text.startswith(target_text):
                    composed_text.append(source_text)
                else:
                    # Merge conflict
                    composed_text.append('<<<<<<< ++ {0} '.format(source_text))
                    composed_text.append('======= ++ {0} '.format(target_text))
                    composed_text.append('>>>>>>>')
                    has_conflict = True
            else:
                if target_text.startswith(source_text):
                    composed_text.append(target_text)
                else:
                    # Merge conflict
                    composed_text.append('<<<<<<< ++ {0} '.format(source_text))
                    composed_text.append('======= ++ {0} '.format(target_text))
                    composed_text.append('>>>>>>>')
                    has_conflict = True
            source = next(diff1, None)
            target = next(diff2, None)
        elif source_status == DELETION and target_status == DELETION:
            # Possible merge conflict
            merge_conflict = False
            if len(source_text) > len(target_text):
                if source_text.startswith(target_text):
                    # Peek target to delete preserved text
                    source_text = source_text[len(target_text):]
                    source = (source_status, source_text)
                    target = next(diff2, None)
                else:
                    merge_conflict = True
            elif len(target_text) > len(source_text):
                if target_text.startswith(source_text):
                    target_text = target_text[len(source_text):]
                    target = (target_status, target_text)
                    source = next(diff1, None)
                else:
                    merge_conflict = True
            else:
                if target_text == source_text:
                    # Both source and target remove the same text
                    source = next(diff1, None)
                    target = next(diff2, None)
                else:
                    merge_conflict = True
            if merge_conflict:
                composed_text.append('<<<<<<< -- {0} '.format(source_text))
                composed_text.append('======= -- {0} '.format(target_text))
                composed_text.append('>>>>>>>')
                has_conflict = True

    while source is not None:
        source_status, source_text = source
        assert source_status == ADDITION or source_status == PRESERVED
        if source_status == ADDITION:
            composed_text.append(source_text)
        source = next(diff1, None)

    while target is not None:
        target_status, target_text = target
        # fix assertion; source_status ---> target_status
        #assert target_status == ADDITION or source_status == PRESERVED
        assert target_status == ADDITION or target_status == PRESERVED 
        if target_status == ADDITION:
            composed_text.append(target_text)
        target = next(diff2, None)

    return (''.join(composed_text), has_conflict)