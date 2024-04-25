import numpy as np
from matplotlib import pyplot as plt
from sklearn.metrics import roc_curve, auc, roc_auc_score


def plot_roc_auc_multilabel(y_true, y_pred_proba, class_labels):
    # Calculate ROC AUC score for each label
    roc_auc_scores = []
    for i in range(len(y_pred_proba)):
        roc_auc_scores.append(roc_auc_score(y_true[:, i], y_pred_proba[i][:, 1]))

    # Calculate ROC curves and AUC scores for each label
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    for i in range(len(y_true[0])):
        fpr[i], tpr[i], _ = roc_curve(y_true[:, i], y_pred_proba[i][:, 1])
        roc_auc[i] = auc(fpr[i], tpr[i])

    # Compute micro-average ROC curve and ROC AUC score
    fpr_micro, tpr_micro, _ = roc_curve(y_true.ravel(), np.hstack([y_pred[:, 1] for y_pred in y_pred_proba]))
    roc_auc_micro = auc(fpr_micro, tpr_micro)

    # Compute macro-average ROC curve and ROC AUC score
    all_fpr = np.unique(np.concatenate([fpr[i] for i in range(len(y_true[0]))]))
    mean_tpr = np.zeros_like(all_fpr)
    for i in range(len(y_true[0])):
        mean_tpr += np.interp(all_fpr, fpr[i], tpr[i])
    mean_tpr /= len(y_true[0])
    fpr_macro = all_fpr
    tpr_macro = mean_tpr
    roc_auc_macro = auc(fpr_macro, tpr_macro)

    # Plot ROC curves for each label
    plt.figure(figsize=(8, 6))
    colors = ['#1696d2', '#fdbf11', '#ec008b', '#55b748', '#5c5859', '#db2b27']
    for i, color in zip(range(len(y_true[0])), colors):
        plt.plot(fpr[i], tpr[i], color=color, lw=2,
                 label=f'{class_labels[i]} (AUC = {roc_auc_scores[i]:.2f})')

    # Plot micro-average ROC curve
    plt.plot(fpr_micro, tpr_micro, color='deeppink',
             linestyle=':', linewidth=4,
             label=f'micro-average ROC curve (AUC = {roc_auc_micro:.2f})')

    # Plot macro-average ROC curve
    plt.plot(fpr_macro, tpr_macro, color='navy',
             linestyle=':', linewidth=4,
             label=f'macro-average ROC curve (AUC = {roc_auc_macro:.2f})')

    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Extension of ROC to Multi-label Classification')
    plt.legend(loc='lower right')
    plt.grid(True)
    plt.show()


def display_features_importance(model, type: str):
    importances = model.named_steps[type].feature_importances_
    features = (numerical_variables +
                model.named_steps['preprocessor'].transformers_[1][1].named_steps[
                    'encoder'].get_feature_names_out(categorical_variables).tolist())
    feature_importances = pd.Series(importances, index=features).sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=feature_importances, y=feature_importances.index, ax=ax)
    ax.set(xlabel='Level of importance', ylabel='Features')
    plt.title('Feature Importance')
    plt.show()
