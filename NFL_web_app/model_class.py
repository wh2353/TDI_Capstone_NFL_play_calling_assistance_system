from sklearn.base import BaseEstimator, RegressorMixin, TransformerMixin
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline

class linear_plus_nonlinear(BaseEstimator, TransformerMixin):
	'''
	class to define the model
	'''
	def __init__(self, alpha=1, max_depth=1, min_samples_leaf=1, n_estimators=100):
		
		self = self
		self.alpha = alpha
		self.max_depth = max_depth
		self.min_samples_leaf = min_samples_leaf
		self.n_estimators = n_estimators
		

	def fit(self, X, y):
		ridge = Ridge(alpha=self.alpha)
		rf = RandomForestRegressor(max_depth=self.max_depth, min_samples_leaf=self.min_samples_leaf, n_estimators=self.n_estimators)
		self.linear_fit = ridge.fit(X, y)
		residual = y - (self.linear_fit.predict(X))
		#print(f"residual shape is {residual.shape}")
		self.nonlinear_fit = rf.fit(X, residual)
		
		return self

	def predict(self, X):
		return self.linear_fit.predict(X) + self.nonlinear_fit.predict(X)