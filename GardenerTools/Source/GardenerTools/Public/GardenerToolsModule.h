#pragma once

#include "Modules/ModuleManager.h"
#include "URegrowCommand.h"

class FGardenerToolsModule : public FDefaultGameModuleImpl {
public:
	virtual void StartupModule() override;

	virtual bool IsGameModule() const override { return true; }	
};