import pandas as pd
from datasets import load_dataset

from sentence_transformers import SentenceTransformer

from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import classification_report
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression


label_names = [
            "activate_my_card",
            "age_limit",
            "apple_pay_or_google_pay",
            "atm_support",
            "automatic_top_up",
            "balance_not_updated_after_bank_transfer",
            "balance_not_updated_after_cheque_or_cash_deposit",
            "beneficiary_not_allowed",
            "cancel_transfer",
            "card_about_to_expire",
            "card_acceptance",
            "card_arrival",
            "card_delivery_estimate",
            "card_linking",
            "card_not_working",
            "card_payment_fee_charged",
            "card_payment_not_recognised",
            "card_payment_wrong_exchange_rate",
            "card_swallowed",
            "cash_withdrawal_charge",
            "cash_withdrawal_not_recognised",
            "change_pin",
            "compromised_card",
            "contactless_not_working",
            "country_support",
            "declined_card_payment",
            "declined_cash_withdrawal",
            "declined_transfer",
            "direct_debit_payment_not_recognised",
            "disposable_card_limits",
            "edit_personal_details",
            "exchange_charge",
            "exchange_rate",
            "exchange_via_app",
            "extra_charge_on_statement",
            "failed_transfer",
            "fiat_currency_support",
            "get_disposable_virtual_card",
            "get_physical_card",
            "getting_spare_card",
            "getting_virtual_card",
            "lost_or_stolen_card",
            "lost_or_stolen_phone",
            "order_physical_card",
            "passcode_forgotten",
            "pending_card_payment",
            "pending_cash_withdrawal",
            "pending_top_up",
            "pending_transfer",
            "pin_blocked",
            "receiving_money",
            "Refund_not_showing_up",
            "request_refund",
            "reverted_card_payment?",
            "supported_cards_and_currencies",
            "terminate_account",
            "top_up_by_bank_transfer_charge",
            "top_up_by_card_charge",
            "top_up_by_cash_or_cheque",
            "top_up_failed",
            "top_up_limits",
            "top_up_reverted",
            "topping_up_by_card",
            "transaction_charged_twice",
            "transfer_fee_charged",
            "transfer_into_account",
            "transfer_not_received_by_recipient",
            "transfer_timing",
            "unable_to_verify_identity",
            "verify_my_identity",
            "verify_source_of_funds",
            "verify_top_up",
            "virtual_card_not_working",
            "visa_or_mastercard",
            "why_verify_identity",
            "wrong_amount_of_cash_received",
            "wrong_exchange_rate_for_cash_withdrawal"]

class Pipeline:

    def load_dataset(self):
        return load_dataset("PolyAI/banking77", revision="main") # taking the data from the main branch
    
    def train(self):
        dataset = self.load_dataset()
        train_data = pd.DataFrame(dataset['train'])
        test_data = pd.DataFrame(dataset['test'])

        embeddings_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        
        train_text_lists = train_data.text.tolist()
        test_text_lists = test_data.text.tolist()
        print("Encoding embeddings")
        train_embeddings = embeddings_model.encode(train_text_lists, show_progress_bar=True)
        test_embeddings = embeddings_model.encode(test_text_lists, show_progress_bar=True)

        X_train, X_val, y_train, y_val = train_test_split(
            train_embeddings, train_data['label_name'], test_size=0.2, random_state=0)
        
        params = {
            "n_neighbors": [3, 5, 7, 9, 11, 13, 15],
            "weights": ["distance", "uniform"],
            "metric": ["cosine", "euclidean" ]
        }

        print("Training KNN")
        knn = KNeighborsClassifier(n_neighbors=5, weights='distance', metric='cosine')
        knn.fit(X_train, y_train)
        y_pred = knn.predict(X_val)
        print(classification_report(y_val, y_pred))


        knn.predict(embeddings_model.encode("I still haven't recieved my card, when will it be ready?").reshape(1, -1))



if __name__ == "__main__":
    import fire
    fire.Fire(Pipeline)