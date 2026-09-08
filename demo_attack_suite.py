"""Offline demonstrations through the real compiler; no Binance calls."""
from tradegate.service import arena

def main():
    result = arena()
    print('KACHING! ADVERSARIAL ARENA\n' + result['label'])
    for attack in result['attacks']:
        print(('CONTAINED' if attack['contained'] else 'FAILED') + ' — ' + attack['name'])
    print(f"{result['passed']} / {result['total']} ATTACKS CONTAINED")
    return 0 if result['passed'] == result['total'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
