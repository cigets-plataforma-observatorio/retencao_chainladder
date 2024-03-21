def calcular_mape(cl_model):
    mape = (abs(cl_model.full_triangle_ - cl_model.full_expectation_) / cl_model.full_triangle_)
    mape = mape[mape.valuation <= '2024'].to_frame()
    return mape
