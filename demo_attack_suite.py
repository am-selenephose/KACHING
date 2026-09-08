"""Offline deterministic demonstrations through real KACHING policy/verifier code."""
from tradegate.service import arena, enforcement_arena


def main() -> int:
    policy = arena()
    authz = enforcement_arena()
    print('KACHING! ADVERSARIAL ARENA\n' + policy['label'])
    for attack in policy['attacks']:
        print(('CONTAINED' if attack['contained'] else 'FAILED') + ' — ' + attack['name'])
    print(f"{policy['passed']} / {policy['total']} POLICY ATTACKS CONTAINED\n")
    print('KACHING! AUTHORIZATION BYPASS GAUNTLET\n' + authz['label'])
    print('BASELINE — ' + authz['baseline'])
    for bypass in authz['bypasses']:
        print(('REJECTED' if bypass['rejected'] else 'FAILED') + ' — ' + bypass['name'] + ' — ' + bypass['reason'])
    print(f"{authz['passed']} / {authz['total']} AUTHORIZATION BYPASSES REJECTED")
    return 0 if policy['passed'] == policy['total'] and authz['passed'] == authz['total'] and authz['baseline'] == 'VALID' else 1


if __name__ == '__main__':
    raise SystemExit(main())
