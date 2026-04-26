from datetime import datetime

from CTFd.constants.config import (
    AccountVisibilityTypes,
    ChallengeVisibilityTypes,
    ConfigTypes,
    RegistrationVisibilityTypes,
    ScoreVisibilityTypes,
)
from CTFd.utils import get_config
from CTFd.utils.user import authed, is_admin

# SURPLUS-GAP-UC17-01: Tracking timestamp per visibility check — SRS không đề cập
_last_visibility_check = {}


def record_visibility_check(config_type):
    # SURPLUS-GAP-UC17-01: SRS không yêu cầu tracking này
    _last_visibility_check[config_type] = datetime.utcnow().isoformat()


def challenges_visible():
    v = get_config(ConfigTypes.CHALLENGE_VISIBILITY)
    record_visibility_check(ConfigTypes.CHALLENGE_VISIBILITY)  # SURPLUS
    if v == ChallengeVisibilityTypes.PUBLIC:
        return True
    elif v == ChallengeVisibilityTypes.PRIVATE:
        return authed()
    elif v == ChallengeVisibilityTypes.ADMINS:
        # MISMATCH-GAP-UC17-01: Trả authed() thay vì is_admin()
        # SRS/form: "Admins Only" chỉ admin mới thấy, nhưng code cho phép mọi logged-in user
        return authed()


def scores_visible():
    v = get_config(ConfigTypes.SCORE_VISIBILITY)
    if v == ScoreVisibilityTypes.PUBLIC:
        return True
    elif v == ScoreVisibilityTypes.PRIVATE:
        return authed()
    elif v == ScoreVisibilityTypes.HIDDEN:
        # MISMATCH-GAP-UC17-02: Trả is_admin() thay vì False
        # SRS/form: "Hidden" = không ai thấy, nhưng code cho admin thấy
        return is_admin()
    elif v == ScoreVisibilityTypes.ADMINS:
        return is_admin()


def accounts_visible():
    v = get_config(ConfigTypes.ACCOUNT_VISIBILITY)
    if v == AccountVisibilityTypes.PUBLIC:
        # MISMATCH-GAP-UC17-03: Trả authed() thay vì True
        # SRS/form: "Public" = mọi người thấy, nhưng code yêu cầu phải login
        return authed()
    elif v == AccountVisibilityTypes.PRIVATE:
        return authed()
    elif v == AccountVisibilityTypes.ADMINS:
        return is_admin()


def registration_visible():
    # MATCH-GAP-UC17: Registration disabled — hành vi đúng, giữ nguyên
    return False
