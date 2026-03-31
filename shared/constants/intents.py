from enum import Enum

class Intent(str, Enum):
    INFO_PRODUIT = "INFO_PRODUIT"
    INFO_SERVICE = "INFO_SERVICE"
    DEPOT_RECLAMATION = "DEPOT_RECLAMATION"
    SUIVI_RECLAMATION = "SUIVI_RECLAMATION"
    VALIDATION_WALLET = "VALIDATION_WALLET"
    DEMANDE_AGENT = "DEMANDE_AGENT"
    SALUTATION = "SALUTATION"
    HORS_SUJET = "HORS_SUJET"
    UNKNOWN = "UNKNOWN"

class ComplaintType(str, Enum):
    VIREMENT_NON_RECU = "virement_non_recu"
    DEBIT_INJUSTIFIE = "debit_injustifie"
    PROBLEME_CARTE = "probleme_carte"
    FRAIS_CONTESTES = "frais_contestes"
    BLOCAGE_COMPTE = "blocage_compte"
    AUTRE = "autre"

INTENT_DESCRIPTIONS = {
    Intent.INFO_PRODUIT: "Question sur les produits bancaires",
    Intent.INFO_SERVICE: "Question sur les services (horaires, agences...)",
    Intent.DEPOT_RECLAMATION: "Déposer une nouvelle réclamation",
    Intent.SUIVI_RECLAMATION: "Vérifier le statut d'une réclamation",
    Intent.VALIDATION_WALLET: "Valider le compte Click Wallet",
    Intent.DEMANDE_AGENT: "L'utilisateur veut parler à un humain",
    Intent.SALUTATION: "Salutation ou remerciement",
    Intent.HORS_SUJET: "Demande sans rapport avec la banque",
}
