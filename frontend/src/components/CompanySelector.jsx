import React, { useEffect, useState } from "react";
import api from "../services/api";

export function CompanySelector({ value, onChange }) {
  const [companies, setCompanies] = useState([]);
  useEffect(() => {
    api.get("/companies/")
      .then((response) => setCompanies((response.data || []).filter((company) => company.activo)))
      .catch(() => setCompanies([]));
  }, []);

  return (
    <label className="block text-sm font-semibold text-slate-700">
      Empresa *
      <select
        value={value || ""}
        onChange={(event) => onChange(event.target.value ? Number(event.target.value) : null)}
        required
        className="mt-2 h-11 w-full rounded-xl border border-slate-200 bg-white px-3"
      >
        <option value="">Seleccionar empresa</option>
        {companies.map((company) => (
          <option key={company.id} value={company.id}>{company.nombre}</option>
        ))}
      </select>
    </label>
  );
}
