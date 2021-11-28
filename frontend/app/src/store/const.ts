export enum Status {
  NONE,
  LOADING,
  REFRESHING,
  PARTIALLY_LOADED,
  LOADED
}

export enum Section {
  NONE,
  ASSET_MOVEMENT,
  TRADES,
  TX,
  DEFI_COMPOUND_BALANCES,
  DEFI_COMPOUND_HISTORY,
  DEFI_OVERVIEW,
  DEFI_AAVE_BALANCES,
  DEFI_AAVE_HISTORY,
  DEFI_BORROWING_HISTORY,
  DEFI_LENDING,
  DEFI_LENDING_HISTORY,
  DEFI_BORROWING,
  DEFI_BALANCES,
  DEFI_DSR_BALANCES,
  DEFI_DSR_HISTORY,
  DEFI_MAKERDAO_VAULT_DETAILS,
  DEFI_MAKERDAO_VAULTS,
  DEFI_YEARN_VAULTS_HISTORY,
  DEFI_YEARN_VAULTS_BALANCES,
  BLOCKCHAIN_BTC,
  BLOCKCHAIN_ETH,
  BLOCKCHAIN_KSM,
  BLOCKCHAIN_DOT,
  BLOCKCHAIN_AVAX,
  DEFI_UNISWAP_BALANCES,
  DEFI_UNISWAP_TRADES,
  DEFI_UNISWAP_EVENTS,
  STAKING_ETH2,
  STAKING_ETH2_DEPOSITS,
  STAKING_ADEX,
  STAKING_ADEX_HISTORY,
  DEFI_AIRDROPS,
  LEDGER_ACTIONS,
  PRICES,
  EXCHANGES,
  MANUAL_BALANCES,
  L2_LOOPRING_BALANCES,
  DEFI_BALANCER_BALANCES,
  DEFI_BALANCER_TRADES,
  DEFI_BALANCER_EVENTS,
  DEFI_YEARN_VAULTS_V2_HISTORY,
  DEFI_YEARN_VAULTS_V2_BALANCES,
  DEFI_SUSHISWAP_BALANCES,
  DEFI_SUSHISWAP_TRADES,
  DEFI_SUSHISWAP_EVENTS,
  DEFI_LIQUITY_BALANCES,
  DEFI_LIQUITY_EVENTS,
  NON_FUNGIBLE_BALANCES,
  DEFI_LIQUITY_STAKING,
  DEFI_LIQUITY_STAKING_EVENTS
}

export const defiSections: Section[] = [
  Section.DEFI_COMPOUND_BALANCES,
  Section.DEFI_COMPOUND_HISTORY,
  Section.DEFI_OVERVIEW,
  Section.DEFI_AAVE_BALANCES,
  Section.DEFI_AAVE_HISTORY,
  Section.DEFI_BORROWING_HISTORY,
  Section.DEFI_LENDING,
  Section.DEFI_LENDING_HISTORY,
  Section.DEFI_BORROWING,
  Section.DEFI_BALANCES,
  Section.DEFI_DSR_BALANCES,
  Section.DEFI_DSR_HISTORY,
  Section.DEFI_MAKERDAO_VAULT_DETAILS,
  Section.DEFI_MAKERDAO_VAULTS,
  Section.DEFI_YEARN_VAULTS_BALANCES,
  Section.DEFI_YEARN_VAULTS_HISTORY,
  Section.DEFI_YEARN_VAULTS_V2_BALANCES,
  Section.DEFI_YEARN_VAULTS_V2_HISTORY,
  Section.DEFI_LIQUITY_BALANCES,
  Section.DEFI_LIQUITY_EVENTS,
  Section.DEFI_UNISWAP_BALANCES,
  Section.DEFI_UNISWAP_TRADES,
  Section.DEFI_UNISWAP_EVENTS,
  Section.DEFI_SUSHISWAP_BALANCES,
  Section.DEFI_SUSHISWAP_TRADES,
  Section.DEFI_SUSHISWAP_EVENTS,
  Section.DEFI_AIRDROPS
];
