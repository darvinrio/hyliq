# HyperLiquid L1 Schema

```ts
type MiscEvent = {
  time: string;
  hash: string;
  inner: MiscEventInner;
}

type MiscEventInner = CDeposit | Delegation | CWithdrawal | ValidatorRewards | Funding | LedgerUpdate;

type CDeposit = {
  user: string;
  amount: number;
}

type Delegation = {
  user: string;
  validator: string;
  amount: number;
  is_undelegate: boolean;
}

type CWithdrawal = {
  user: string;
  amount: number;
  is_finalized: boolean;
}

type ValidatorRewards = {
  validator_to_reward: Array<[string, number]>;
}

type Funding {
  coin: string;
  usdc: number;
  szi: number;
  fundingRate: number;
  nSamples: number;
}

type LedgerUpdate = {
  users: Array<string>;
  delta: LedgerDelta;
}

// InternalTransfer means Perp USDC transfer
// RewardsClaim is for builder and referrer fees
// Deposit/Withdraw refer to Arbitrum USDC bridge
type LedgerDelta = Withdraw 
  | Deposit
  | VaultCreate
  | VaultDeposit
  | VaultWithdraw
  | VaultDistribution
  | VaultLeaderCommission
  | Liquidation
  | InternalTransfer
  | SubAccountTransfer
  | SpotTransfer
  | SpotGenesis
  | RewardsClaim
  | AccountActivationGas
  | PerpDexClassTransfer
  | DeployGasAuction;
  
type Withdraw = {
  usdc: number;
  nonce: number;
  fee: number;
}

type Deposit = {
  usdc: number;
}

type VaultCreate {
  vault: string;
  usdc: number;
  fee: number;
}

type VaultWithdraw {
  vault: string;
  user: string;
  requestedUsd: number;
  commission: number;
  closingCost: number;
  basis: number;
}

type VaultDistribution {
  vault: string;
  usdc: number;
}

type Liquidation {
  liquidatedNtlPos: number;
  accountValue: number;
  leverageType: string;
  liquidatedPositions: Array<LiquidatedPosition>;
}

type LiquidatedPosition {
  coin: string;
  szi: number;
}
 
type InternalTransfer {
  usdc: number;
  user: string;
  destination: string;
  fee: number;
}

type AccountClassTransfer {
  usdc: number;
  toPerp: boolean;
}

type SubAccountTransfer {
  usdc: number;
  user: string;
  destination: string;
}

type SpotTransfer {
  token: string;
  amount: number;
  usdcValue: number;
  user: string;
  destination: string;
  fee: number;
  nativeTokenFee: number;
}

type SpotGenesis {
  token: string;
  amount: number;
}

type RewardsClaim {
  amount: number;
}

type AccountActivationGas {
  amount: number;
  token: string;
}

type PerpDexClassTransfer {
  amount: number;
  token: string;
  dex: string;
  toPerp: boolean;
}

type DeployGasAuction {
  token: string;
  amount: number;
}
```
